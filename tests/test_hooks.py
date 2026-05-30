"""
L0: ODD 훅 테스트 인프라 — 모든 훅이 예측 가능하게 동작함을 자동으로 검증한다
L1: 각 활성 훅의 PASS(exit 0) / BLOCK(exit 2) 시나리오를 커버하는 통합 테스트
L2: Python unittest + subprocess 기반, JSON stdin 주입으로 훅 실행
L3: tests/test_hooks.py — hooks/*.py 에 stdin JSON을 파이프해 exit code 검증

실행: python tests/test_hooks.py
      python -m pytest tests/test_hooks.py -v
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

# ─── 경로 설정 ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
HOOKS_DIR = ROOT / "hooks"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _run_hook(hook_name: str, stdin_payload: dict, env: dict | None = None) -> int:
    """
    훅을 subprocess로 실행하고 exit code를 반환한다.
    stdin에 JSON payload를 주입한다.
    """
    hook_path = HOOKS_DIR / hook_name
    if not hook_path.exists():
        raise FileNotFoundError(f"Hook not found: {hook_path}")

    run_env = os.environ.copy()
    if env:
        run_env.update(env)

    result = subprocess.run(
        [sys.executable, str(hook_path)],
        input=json.dumps(stdin_payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=run_env,
        timeout=30,
    )
    return result.returncode


def _fixture(name: str) -> str:
    """fixture 파일의 절대 경로를 반환한다."""
    return str(FIXTURES_DIR / name)


# ─── 1. pyramid_ontology_gate.py 테스트 ──────────────────────────────────────

class TestPyramidOntologyGate(unittest.TestCase):
    """PreToolUse/Edit — L0 선언 없으면 차단"""

    HOOK = "pyramid_ontology_gate.py"

    def _make_payload(self, file_path: str, transcript_path: str) -> dict:
        return {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": file_path,
                "old_string": "a",
                "new_string": "b",
            },
            "transcript_path": transcript_path,
        }

    def test_pass_with_l0_in_transcript(self):
        """L0 선언이 있는 transcript → exit 0 (통과)"""
        payload = self._make_payload(
            "/tmp/some_file.py",
            _fixture("transcript_with_l0.jsonl"),
        )
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_block_without_l0(self):
        """L0 선언 없는 transcript → exit 2 (차단)"""
        payload = self._make_payload(
            "/tmp/some_file.py",
            _fixture("transcript_no_l0.jsonl"),
        )
        self.assertEqual(_run_hook(self.HOOK, payload), 2)

    def test_pass_for_hook_py_file(self):
        """hooks/*.py 수정 → 무한루프 방지 면제 → exit 0"""
        payload = self._make_payload(
            str(HOOKS_DIR / "pyramid_ontology_gate.py"),
            _fixture("transcript_no_l0.jsonl"),
        )
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_for_hooks_json(self):
        """hooks.json 수정 → 설정 파일 면제 → exit 0"""
        payload = self._make_payload(
            str(HOOKS_DIR / "hooks.json"),
            _fixture("transcript_no_l0.jsonl"),
        )
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_no_transcript(self):
        """transcript 없으면 (초기 세션) → exit 0"""
        payload = self._make_payload("/tmp/some_file.py", "/nonexistent/path.jsonl")
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_non_edit_tool(self):
        """Edit 아닌 도구 → 검사 대상 아님 → exit 0"""
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "ls"},
            "transcript_path": _fixture("transcript_no_l0.jsonl"),
        }
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_claude_md_file(self):
        """CLAUDE.md 수정 → 면제 파일 → exit 0"""
        payload = self._make_payload(
            "/some/path/CLAUDE.md",
            _fixture("transcript_no_l0.jsonl"),
        )
        self.assertEqual(_run_hook(self.HOOK, payload), 0)


# ─── 2. ontology_violation_gate.py 테스트 ────────────────────────────────────

class TestOntologyViolationGate(unittest.TestCase):
    """PreToolUse/Edit — violation_registry.json 규칙 적용"""

    HOOK = "ontology_violation_gate.py"

    def test_pass_non_edit_tool(self):
        """Edit 아닌 도구 → 검사 대상 아님 → exit 0"""
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "ls"},
        }
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_empty_content(self):
        """content 없음 → exit 0"""
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": "/tmp/test.py", "content": ""},
        }
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_normal_py_file(self):
        """일반 .py 파일, 위반 없음 → exit 0"""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/tmp/normal.py",
                "content": "# L0: 테스트 목적\n# L1: 구조\ndef foo():\n    pass\n",
            },
        }
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_block_locked_file_write(self):
        """LOCKED 파일 Write 시도 → evaluator_self_judge_guard 규칙 → exit 2"""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/some/path/EVAL_RUBRIC_LOCKED.md",
                "content": "## Some content\nThis should be blocked.",
            },
        }
        self.assertEqual(_run_hook(self.HOOK, payload), 2)

    def test_pass_unlocked_md_file(self):
        """LOCKED 아닌 .md 파일 → 규칙 미해당 → exit 0"""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/some/path/README.md",
                "content": "## Normal README\nContent here.",
            },
        }
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_invalid_json_input(self):
        """잘못된 JSON 입력 → graceful exit 0"""
        hook_path = HOOKS_DIR / self.HOOK
        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input="not valid json",
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        self.assertEqual(result.returncode, 0)


# ─── 3. destructive_bash_gate.py 테스트 ──────────────────────────────────────

class TestDestructiveBashGate(unittest.TestCase):
    """PreToolUse/Bash — 비가역 명령어 차단"""

    HOOK = "destructive_bash_gate.py"

    def _make_bash_payload(self, command: str) -> dict:
        return {
            "tool_name": "Bash",
            "tool_input": {"command": command},
        }

    def test_pass_safe_command(self):
        """안전한 명령어 → exit 0"""
        payload = self._make_bash_payload("ls -la /tmp")
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_git_command(self):
        """git 명령어 → exit 0"""
        payload = self._make_bash_payload("git status")
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_python_command(self):
        """python 실행 → exit 0"""
        payload = self._make_bash_payload("python -m pytest tests/")
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_block_delete_from(self):
        """DELETE FROM 명령 → exit 2"""
        payload = self._make_bash_payload("sqlite3 db.sqlite 'DELETE FROM users'")
        self.assertEqual(_run_hook(self.HOOK, payload), 2)

    def test_block_drop_table(self):
        """DROP TABLE → exit 2"""
        payload = self._make_bash_payload("sqlite3 db.sqlite 'DROP TABLE items'")
        self.assertEqual(_run_hook(self.HOOK, payload), 2)

    def test_block_rm_db_file(self):
        """rm -rf *.db → exit 2"""
        payload = self._make_bash_payload("rm -rf mydata.db")
        self.assertEqual(_run_hook(self.HOOK, payload), 2)

    def test_block_shutil_rmtree(self):
        """shutil.rmtree 포함 → exit 2"""
        payload = self._make_bash_payload("python -c \"import shutil; shutil.rmtree('.')\"")
        self.assertEqual(_run_hook(self.HOOK, payload), 2)

    def test_block_vacuum(self):
        """VACUUM 명령 → exit 2"""
        payload = self._make_bash_payload("sqlite3 db.sqlite 'VACUUM'")
        self.assertEqual(_run_hook(self.HOOK, payload), 2)

    def test_pass_non_bash_tool(self):
        """Bash 아닌 도구 → exit 0"""
        payload = {"tool_name": "Edit", "tool_input": {"command": "DROP TABLE users"}}
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_empty_command(self):
        """빈 command → exit 0"""
        payload = self._make_bash_payload("")
        self.assertEqual(_run_hook(self.HOOK, payload), 0)


# ─── 4. agent_pyramid_gate.py 테스트 ─────────────────────────────────────────

class TestAgentPyramidGate(unittest.TestCase):
    """PreToolUse/Agent — L0 미션 필수"""

    HOOK = "agent_pyramid_gate.py"

    def test_pass_with_l0_mission(self):
        """L0 미션 포함 프롬프트 → exit 0"""
        prompt = (
            "직책: Worker\n"
            "L0 미션: 파일 분석 및 리포트 생성 — 프로젝트 구조를 명확히 이해한다\n"
            "담당 범위: src/ 폴더 전체\n"
            "예산: 제한 없음\n"
            "보고 대상: 상위 에이전트\n"
            "위 내용으로 작업을 진행해줘."
        )
        payload = {
            "tool_name": "Agent",
            "tool_input": {"prompt": prompt, "model": "sonnet"},
        }
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_block_without_l0(self):
        """L0 없는 긴 프롬프트(150자 초과) → exit 2"""
        # MIN_PROMPT_LEN = 150 — 반드시 150자 이상이어야 검사 대상이 됨
        prompt = (
            "이 프로젝트의 모든 파일들을 분석해서 구조적인 문제점을 찾아줘. "
            "코드를 읽고 리팩토링이 필요한 부분을 식별하고 "
            "전체 아키텍처 구조를 파악해서 개선방안을 상세히 제안해줘. "
            "최소 다섯 가지 이상의 개선점을 찾아줘. "
            "결과는 마크다운 형식으로 상세하게 작성해줘. "
            "각 개선점에 대해 우선순위도 함께 제시해줘."
        )
        assert len(prompt) >= 150, f"프롬프트가 너무 짧음: {len(prompt)}자"
        payload = {
            "tool_name": "Agent",
            "tool_input": {"prompt": prompt, "model": "sonnet"},
        }
        self.assertEqual(_run_hook(self.HOOK, payload), 2)

    def test_pass_short_prompt(self):
        """짧은 프롬프트(150자 미만) → 검사 생략 → exit 0"""
        payload = {
            "tool_name": "Agent",
            "tool_input": {"prompt": "파일 읽어줘", "model": "sonnet"},
        }
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_non_agent_tool(self):
        """Agent 아닌 도구 → exit 0"""
        payload = {
            "tool_name": "Bash",
            "tool_input": {"prompt": "no l0 here"},
        }
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_l0_colon_format(self):
        """L0: 포함 → exit 0"""
        prompt = (
            "L0: 코드베이스 분석을 통해 아키텍처 문제를 식별한다\n"
            "역할: Worker\n"
            "담당 범위: 전체 프로젝트\n"
            "이 프로젝트의 구조를 분석하고 개선점을 제안해줘. "
            "최소 다섯 가지 개선점을 찾아줘. 결과는 마크다운으로 작성해줘."
        )
        payload = {
            "tool_name": "Agent",
            "tool_input": {"prompt": prompt, "model": "haiku"},
        }
        self.assertEqual(_run_hook(self.HOOK, payload), 0)


# ─── 5. tdd_enforce_stop.py 테스트 ───────────────────────────────────────────

class TestTddEnforceStop(unittest.TestCase):
    """Stop 훅 — Edit 후 검증 없으면 차단"""

    HOOK = "tdd_enforce_stop.py"

    def _make_payload(self, transcript_path: str) -> dict:
        return {"transcript_path": transcript_path}

    def test_pass_no_edit(self):
        """Edit 없는 세션 → exit 0"""
        payload = self._make_payload(_fixture("transcript_clean.jsonl"))
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_edit_with_verify(self):
        """Edit 후 py_compile 실행 → exit 0"""
        payload = self._make_payload(_fixture("transcript_edit_with_verify.jsonl"))
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_block_edit_no_verify(self):
        """Edit 후 검증 없음 → exit 2"""
        payload = self._make_payload(_fixture("transcript_edit_no_verify.jsonl"))
        self.assertEqual(_run_hook(self.HOOK, payload), 2)

    def test_pass_md_only_edit(self):
        """.md 파일만 편집 → 문서 면제 → exit 0"""
        payload = self._make_payload(_fixture("transcript_md_only_edit.jsonl"))
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_no_transcript(self):
        """transcript 없음 → exit 0"""
        payload = self._make_payload("/nonexistent/path.jsonl")
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_invalid_json(self):
        """잘못된 JSON → graceful exit 0"""
        hook_path = HOOKS_DIR / self.HOOK
        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input="not json",
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        self.assertEqual(result.returncode, 0)


# ─── 6. ontology_learning_enforce_stop.py 테스트 ─────────────────────────────

class TestOntologyLearningEnforceStop(unittest.TestCase):
    """Stop 훅 — tool error 후 ontology-learning 미발동 차단"""

    HOOK = "ontology_learning_enforce_stop.py"

    def _make_payload(self, transcript_path: str) -> dict:
        return {"transcript_path": transcript_path}

    def test_pass_clean_session(self):
        """tool error 없는 정상 세션 → exit 0"""
        payload = self._make_payload(_fixture("transcript_clean.jsonl"))
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_error_with_ontology_learning(self):
        """tool error 있고 ontology-learning 발동 → exit 0"""
        payload = self._make_payload(_fixture("transcript_with_ontology_learning.jsonl"))
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_block_error_without_ontology_learning(self):
        """tool error 있고 ontology-learning 미발동 → exit 2"""
        payload = self._make_payload(_fixture("transcript_with_tool_error.jsonl"))
        self.assertEqual(_run_hook(self.HOOK, payload), 2)

    def test_pass_short_session(self):
        """3개 미만 메시지 → 검사 건너뜀 → exit 0"""
        # transcript_no_l0.jsonl은 4개 메시지지만 tool error 없음
        payload = self._make_payload(_fixture("transcript_no_l0.jsonl"))
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_no_transcript(self):
        """transcript 없음 → exit 0"""
        payload = self._make_payload("/nonexistent/path.jsonl")
        self.assertEqual(_run_hook(self.HOOK, payload), 0)


# ─── 7. websearch_yearguard.py 테스트 ────────────────────────────────────────

class TestWebsearchYearguard(unittest.TestCase):
    """PreToolUse/WebSearch — 현재 연도 없으면 차단"""

    HOOK = "websearch_yearguard.py"

    def _make_payload(self, query: str) -> dict:
        return {
            "tool_name": "WebSearch",
            "tool_input": {"query": query},
        }

    def test_pass_with_current_year(self):
        """현재 연도 포함 → exit 0"""
        import datetime
        year = str(datetime.datetime.now().year)
        payload = self._make_payload(f"Claude API 요금 {year}")
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_with_2026(self):
        """2026 포함 → exit 0"""
        payload = self._make_payload("OpenAI 최신 모델 2026")
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_with_latest_keyword(self):
        """'최신' 포함 → exit 0"""
        payload = self._make_payload("Claude API 최신 요금")
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_with_current_english(self):
        """'current' 포함 → exit 0"""
        payload = self._make_payload("Claude API current pricing")
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_block_without_year(self):
        """연도/최신 없음 → exit 2"""
        payload = self._make_payload("Claude API 요금제")
        self.assertEqual(_run_hook(self.HOOK, payload), 2)

    def test_block_old_general_query(self):
        """오래된 정보 가능성 있는 일반 쿼리 → exit 2"""
        payload = self._make_payload("Python 버전별 차이점")
        self.assertEqual(_run_hook(self.HOOK, payload), 2)

    def test_pass_non_websearch_tool(self):
        """WebSearch 아닌 도구 → exit 0"""
        payload = {
            "tool_name": "Bash",
            "tool_input": {"query": "오래된 쿼리"},
        }
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_today_keyword(self):
        """'today' 포함 → exit 0"""
        payload = self._make_payload("what is Claude's pricing today")
        self.assertEqual(_run_hook(self.HOOK, payload), 0)


# ─── 8. pyramid_guard.py 테스트 (smoke test) ─────────────────────────────────

class TestPyramidGuard(unittest.TestCase):
    """PostToolUse/Edit — 파일 저장 후 L0 위계 검증 (smoke test)"""

    HOOK = "pyramid_guard.py"

    def test_pass_no_file_paths_env(self):
        """CLAUDE_FILE_PATHS 환경변수 없음 → exit 0"""
        payload = {"tool_name": "Edit", "tool_input": {}}
        result = _run_hook(self.HOOK, payload, env={"CLAUDE_FILE_PATHS": ""})
        self.assertEqual(result, 0)

    def test_pass_nonexistent_file(self):
        """존재하지 않는 파일 경로 → graceful exit 0"""
        payload = {"tool_name": "Edit", "tool_input": {}}
        result = _run_hook(self.HOOK, payload, env={"CLAUDE_FILE_PATHS": "/nonexistent/file.py"})
        self.assertEqual(result, 0)

    def test_smoke_with_valid_file(self):
        """
        실제 .py 파일로 smoke test — 훅이 실행되고 0 또는 2를 반환한다.
        이 훅은 L0 위계 분석이 복잡하므로 exit code 값을 단정하지 않고
        프로세스가 정상 종료됨만 확인한다.
        """
        # pyramid_guard.py 자체를 검사 대상으로 사용
        target_file = str(HOOKS_DIR / "pyramid_guard.py")
        payload = {"tool_name": "Edit", "tool_input": {}}
        hook_path = HOOKS_DIR / self.HOOK
        result = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(payload, ensure_ascii=False),
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "CLAUDE_FILE_PATHS": target_file},
            timeout=30,
        )
        # exit code가 0 또는 2이어야 한다 (1은 Python 예외)
        self.assertIn(result.returncode, [0, 2])

    def test_pass_small_file(self):
        """15줄 미만 파일 → 검사 건너뜀 → exit 0"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("# short file\ndef foo():\n    pass\n")
            tmp_path = f.name
        try:
            payload = {"tool_name": "Edit", "tool_input": {}}
            result = _run_hook(self.HOOK, payload, env={"CLAUDE_FILE_PATHS": tmp_path})
            self.assertEqual(result, 0)
        finally:
            os.unlink(tmp_path)


# ─── 9. pptx_validate_hook.py 테스트 ─────────────────────────────────────────

class TestPptxValidateHook(unittest.TestCase):
    """PostToolUse/Bash — PPTX 빌드 후 레이아웃 overflow 검증 (smoke test)"""

    HOOK = "pptx_validate_hook.py"

    def test_pass_non_ppt_command(self):
        """build_*_ppt.py 아닌 명령 → exit 0"""
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "python normal_script.py"},
        }
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_ppt_command_no_output(self):
        """build_*_ppt.py 명령이지만 .pptx 없음 → graceful exit 0"""
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "python /tmp/build_test_ppt.py"},
        }
        # python-pptx 없거나 .pptx 없으면 exit 0 (graceful)
        result = _run_hook(self.HOOK, payload)
        self.assertIn(result, [0, 2])  # 어떤 경우든 1(Python 예외)은 아니어야 함

    def test_pass_empty_payload(self):
        """빈 payload → exit 0"""
        payload = {}
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_graceful_on_import_error(self):
        """python-pptx 없어도 graceful exit 0"""
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "python /nonexistent/build_report_ppt.py"},
        }
        self.assertEqual(_run_hook(self.HOOK, payload), 0)


# ─── 10. assumption_declaration_gate.py 테스트 ───────────────────────────────

class TestAssumptionDeclarationGate(unittest.TestCase):
    """Stop 훅 — 전략 판단 시 가정 미선언 차단"""

    HOOK = "assumption_declaration_gate.py"

    def _make_payload(self, transcript_path: str) -> dict:
        return {"transcript_path": transcript_path, "stop_hook_active": False}

    def test_pass_clean_session(self):
        """전략 판단 없는 정상 세션 → exit 0"""
        payload = self._make_payload(_fixture("transcript_clean.jsonl"))
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_stop_hook_active(self):
        """stop_hook_active=True → 무한루프 방지 → exit 0"""
        payload = {"transcript_path": _fixture("transcript_clean.jsonl"), "stop_hook_active": True}
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_no_transcript(self):
        """transcript 없음 → exit 0"""
        payload = {"transcript_path": "/nonexistent/path.jsonl", "stop_hook_active": False}
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_block_strategic_judgment_without_assumption(self):
        """
        전략 판단 포함 + 가정 선언 없음 → exit 2.
        transcript의 마지막 assistant 메시지에 전략 판단 패턴 주입.
        """
        import tempfile
        transcript = [
            {"message": {"role": "user", "content": [{"type": "text", "text": "시장 분석해줘"}]}},
            {"message": {"role": "assistant", "content": [{"type": "text", "text": (
                "이 시장은 경쟁력 있습니다. "
                "예상 수익은 200건 × $49로 약 1만 달러입니다. "
                "이 방향이 맞다고 판단합니다."
            )}]}},
        ]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        ) as f:
            for entry in transcript:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            tmp_path = f.name
        try:
            payload = {"transcript_path": tmp_path, "stop_hook_active": False}
            self.assertEqual(_run_hook(self.HOOK, payload), 2)
        finally:
            os.unlink(tmp_path)

    def test_pass_strategic_judgment_with_assumption(self):
        """
        전략 판단 있지만 가정 선언도 있음 → exit 0.
        """
        import tempfile
        transcript = [
            {"message": {"role": "user", "content": [{"type": "text", "text": "시장 분석해줘"}]}},
            {"message": {"role": "assistant", "content": [{"type": "text", "text": (
                "[가정 명시]\n"
                "- 가정 1: 전환율 3% → 미검증\n"
                "- 가정 2: 시장 규모 → 미확인\n\n"
                "이 시장은 경쟁력 있습니다. "
                "예상 수익은 200건 × $49로 약 1만 달러입니다."
            )}]}},
        ]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        ) as f:
            for entry in transcript:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            tmp_path = f.name
        try:
            payload = {"transcript_path": tmp_path, "stop_hook_active": False}
            self.assertEqual(_run_hook(self.HOOK, payload), 0)
        finally:
            os.unlink(tmp_path)


# ─── 11. ontology_declare_enforce.py 테스트 ──────────────────────────────────

class TestOntologyDeclareEnforce(unittest.TestCase):
    """Stop 훅 — Edit/Write 전 L0 선언 강제"""

    HOOK = "ontology_declare_enforce.py"

    def _make_payload(self, transcript_path: str) -> dict:
        return {"transcript_path": transcript_path}

    def test_pass_clean_no_edit(self):
        """Edit 없는 세션 → exit 0"""
        payload = self._make_payload(_fixture("transcript_clean.jsonl"))
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_edit_with_l0(self):
        """Edit 있고 L0 선언 있음 → exit 0"""
        payload = self._make_payload(_fixture("transcript_edit_with_verify.jsonl"))
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_no_transcript(self):
        """transcript 없음 → exit 0"""
        payload = self._make_payload("/nonexistent/path.jsonl")
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_block_edit_without_l0(self):
        """
        Edit 있고 L0 선언 없음 → exit 2.
        transcript_edit_no_verify.jsonl에는 L0가 있으므로 L0 없는 전용 transcript 생성.
        """
        import tempfile
        # Edit이 있지만 L0 선언이 없는 transcript
        transcript = [
            {"message": {"role": "user", "content": [{"type": "text", "text": "수정해줘"}]}},
            {"message": {"role": "assistant", "content": [
                {"type": "text", "text": "수정하겠습니다."},
                {"type": "tool_use", "id": "t1", "name": "Edit", "input": {
                    "file_path": "/tmp/sample.py",
                    "old_string": "a",
                    "new_string": "b",
                }},
            ]}},
            {"message": {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": [{"type": "text", "text": "OK"}]},
            ]}},
            {"message": {"role": "assistant", "content": [
                {"type": "text", "text": "수정 완료"},
            ]}},
        ]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        ) as f:
            for entry in transcript:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            tmp_path = f.name
        try:
            payload = self._make_payload(tmp_path)
            self.assertEqual(_run_hook(self.HOOK, payload), 2)
        finally:
            os.unlink(tmp_path)


# ─── 12. git_push_enforce_stop.py 테스트 (smoke test) ────────────────────────

class TestGitPushEnforceStop(unittest.TestCase):
    """Stop 훅 — Edit 후 git push 강제 (git 상태 의존 smoke test)"""

    HOOK = "git_push_enforce_stop.py"

    def test_pass_no_edit_in_session(self):
        """Edit 없는 세션 → exit 0 (git 상태 무관)"""
        payload = {"transcript_path": _fixture("transcript_clean.jsonl")}
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_pass_no_transcript(self):
        """transcript 없음 → exit 0"""
        payload = {"transcript_path": "/nonexistent/path.jsonl"}
        self.assertEqual(_run_hook(self.HOOK, payload), 0)

    def test_smoke_with_edit_session(self):
        """
        Edit 있는 세션 → git 상태에 따라 0 또는 2.
        프로세스가 정상 종료됨만 확인 (1은 Python 예외이므로 허용 안 함).
        """
        payload = {"transcript_path": _fixture("transcript_edit_with_verify.jsonl")}
        result = _run_hook(self.HOOK, payload)
        self.assertIn(result, [0, 2])


# ─── 13. 훅 등록 일관성 검사 ─────────────────────────────────────────────────

class TestHookRegistryConsistency(unittest.TestCase):
    """hooks.json 등록과 .py 파일 목록의 일관성 검증"""

    def test_all_registered_hooks_exist_as_files(self):
        """hooks.json에 등록된 모든 훅 .py 파일이 실제로 존재해야 한다."""
        hooks_json = HOOKS_DIR / "hooks.json"
        with open(hooks_json, encoding="utf-8") as f:
            data = json.load(f)

        registered = set()
        for phase_hooks in data.get("hooks", {}).values():
            if isinstance(phase_hooks, list):
                for entry in phase_hooks:
                    if isinstance(entry, dict):
                        # 단일 훅 명세
                        for h in entry.get("hooks", []):
                            cmd = h.get("command", "")
                            py_name = _extract_hook_filename(cmd)
                            if py_name:
                                registered.add(py_name)

        missing = []
        for name in registered:
            if not (HOOKS_DIR / name).exists():
                missing.append(name)

        self.assertEqual(
            missing, [],
            f"hooks.json에 등록됐지만 파일이 없는 훅: {missing}"
        )

    def test_hook_count_reasonable(self):
        """등록된 훅 수가 합리적 범위(5~20개)에 있어야 한다."""
        hooks_json = HOOKS_DIR / "hooks.json"
        with open(hooks_json, encoding="utf-8") as f:
            data = json.load(f)

        registered = set()
        for phase_hooks in data.get("hooks", {}).values():
            if isinstance(phase_hooks, list):
                for entry in phase_hooks:
                    if isinstance(entry, dict):
                        for h in entry.get("hooks", []):
                            cmd = h.get("command", "")
                            py_name = _extract_hook_filename(cmd)
                            if py_name:
                                registered.add(py_name)

        count = len(registered)
        self.assertGreaterEqual(count, 5, f"등록 훅이 너무 적음: {count}")
        self.assertLessEqual(count, 20, f"등록 훅이 너무 많음: {count}")


def _extract_hook_filename(command: str) -> str | None:
    """
    hooks.json command 문자열에서 .py 파일명을 추출한다.
    예: "python \"${CLAUDE_PLUGIN_ROOT}/hooks/pyramid_guard.py\""
        → "pyramid_guard.py"
    """
    import re
    m = re.search(r'hooks[/\\](\w+\.py)', command)
    return m.group(1) if m else None


# ─── 14. config_loader.py 테스트 ─────────────────────────────────────────────

class TestConfigLoader(unittest.TestCase):
    """
    hooks/config_loader.py 단위 테스트.
    .odd/config.yaml 유무 / severity 설정 / off 설정 → exit code 분기 검증.
    """

    def _loader_module(self):
        """config_loader 모듈을 동적으로 import."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "config_loader",
            str(HOOKS_DIR / "config_loader.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_config_loader_importable(self):
        """config_loader.py가 py_compile 없이 import 가능해야 한다."""
        mod = self._loader_module()
        self.assertTrue(hasattr(mod, "load_project_config"))
        self.assertTrue(hasattr(mod, "get_exit_code"))
        self.assertTrue(hasattr(mod, "is_path_allowlisted"))

    def test_default_when_no_config_file(self):
        """
        .odd/config.yaml 없을 때 기본값(block) 반환.
        CLAUDE_PROJECT_DIR을 존재하지 않는 경로로 설정.
        """
        import importlib
        mod = self._loader_module()
        orig_env = os.environ.copy()
        try:
            os.environ["CLAUDE_PROJECT_DIR"] = "/nonexistent/project/path"
            cfg = mod.load_project_config("tdd_enforce_stop")
            self.assertEqual(cfg["severity"], "block")
            self.assertEqual(cfg["allowlist_paths"], [])
            self.assertFalse(cfg["config_found"])
        finally:
            os.environ.clear()
            os.environ.update(orig_env)

    def test_warn_severity_from_config(self):
        """
        config.yaml에 warn 설정된 훅 → severity "warn" 반환.
        임시 .odd/config.yaml 생성 후 테스트.
        """
        import tempfile
        mod = self._loader_module()
        orig_env = os.environ.copy()

        with tempfile.TemporaryDirectory() as tmpdir:
            odd_dir = Path(tmpdir) / ".odd"
            odd_dir.mkdir()
            config_file = odd_dir / "config.yaml"
            config_file.write_text(
                "version: 1\n"
                "hooks:\n"
                "  tdd_enforce_stop: warn\n"
                "  ontology_learning_enforce_stop: warn\n"
                "allowlist:\n"
                "  paths:\n"
                "    - \"tests/**\"\n",
                encoding="utf-8",
            )
            try:
                os.environ["CLAUDE_PROJECT_DIR"] = tmpdir
                cfg = mod.load_project_config("tdd_enforce_stop")
                self.assertEqual(cfg["severity"], "warn")
                self.assertTrue(cfg["config_found"])
                self.assertIn("tests/**", cfg["allowlist_paths"])
            finally:
                os.environ.clear()
                os.environ.update(orig_env)

    def test_off_severity_returns_exit_0(self):
        """
        off 설정된 훅 → get_exit_code() → 0 반환 (차단하지 않음).
        """
        import tempfile
        mod = self._loader_module()
        orig_env = os.environ.copy()

        with tempfile.TemporaryDirectory() as tmpdir:
            odd_dir = Path(tmpdir) / ".odd"
            odd_dir.mkdir()
            config_file = odd_dir / "config.yaml"
            config_file.write_text(
                "version: 1\n"
                "hooks:\n"
                "  websearch_yearguard: off\n",
                encoding="utf-8",
            )
            try:
                os.environ["CLAUDE_PROJECT_DIR"] = tmpdir
                exit_code = mod.get_exit_code("websearch_yearguard", default_exit=2)
                self.assertEqual(exit_code, 0)
            finally:
                os.environ.clear()
                os.environ.update(orig_env)

    def test_block_severity_returns_default_exit(self):
        """
        block 설정된 훅 → get_exit_code() → default_exit(2) 반환.
        """
        import tempfile
        mod = self._loader_module()
        orig_env = os.environ.copy()

        with tempfile.TemporaryDirectory() as tmpdir:
            odd_dir = Path(tmpdir) / ".odd"
            odd_dir.mkdir()
            config_file = odd_dir / "config.yaml"
            config_file.write_text(
                "version: 1\n"
                "hooks:\n"
                "  pyramid_ontology_gate: block\n",
                encoding="utf-8",
            )
            try:
                os.environ["CLAUDE_PROJECT_DIR"] = tmpdir
                exit_code = mod.get_exit_code("pyramid_ontology_gate", default_exit=2)
                self.assertEqual(exit_code, 2)
            finally:
                os.environ.clear()
                os.environ.update(orig_env)

    def test_unknown_hook_defaults_to_block(self):
        """
        config.yaml에 없는 훅명 → 기본값(block) 반환.
        """
        import tempfile
        mod = self._loader_module()
        orig_env = os.environ.copy()

        with tempfile.TemporaryDirectory() as tmpdir:
            odd_dir = Path(tmpdir) / ".odd"
            odd_dir.mkdir()
            config_file = odd_dir / "config.yaml"
            config_file.write_text(
                "version: 1\n"
                "hooks:\n"
                "  some_other_hook: warn\n",
                encoding="utf-8",
            )
            try:
                os.environ["CLAUDE_PROJECT_DIR"] = tmpdir
                cfg = mod.load_project_config("tdd_enforce_stop")  # 등록 안 된 훅
                self.assertEqual(cfg["severity"], "block")
            finally:
                os.environ.clear()
                os.environ.update(orig_env)

    def test_allowlist_path_matching(self):
        """
        allowlist에 등록된 경로 패턴 → is_path_allowlisted() → True.
        등록되지 않은 경로 → False.
        """
        import tempfile
        mod = self._loader_module()
        orig_env = os.environ.copy()

        with tempfile.TemporaryDirectory() as tmpdir:
            odd_dir = Path(tmpdir) / ".odd"
            odd_dir.mkdir()
            config_file = odd_dir / "config.yaml"
            config_file.write_text(
                "version: 1\n"
                "hooks:\n"
                "  tdd_enforce_stop: warn\n"
                "allowlist:\n"
                "  paths:\n"
                "    - \"tests/**\"\n"
                "    - \".odd/**\"\n",
                encoding="utf-8",
            )
            try:
                os.environ["CLAUDE_PROJECT_DIR"] = tmpdir
                # 허용 경로
                self.assertTrue(mod.is_path_allowlisted(
                    f"{tmpdir}/tests/test_foo.py", "tdd_enforce_stop"
                ))
                # 허용되지 않는 경로
                self.assertFalse(mod.is_path_allowlisted(
                    f"{tmpdir}/src/main.py", "tdd_enforce_stop"
                ))
            finally:
                os.environ.clear()
                os.environ.update(orig_env)

    def test_py_compile_passes(self):
        """config_loader.py 자체가 문법 오류 없이 컴파일되어야 한다."""
        import py_compile
        try:
            py_compile.compile(str(HOOKS_DIR / "config_loader.py"), doraise=True)
        except py_compile.PyCompileError as e:
            self.fail(f"config_loader.py 컴파일 실패: {e}")


# ─── 진입점 ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # 결과를 verbosely 출력
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    # CI에서 비제로 exit code로 실패 표시
    sys.exit(0 if result.wasSuccessful() else 1)
