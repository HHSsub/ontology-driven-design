# /frozen-exe — Python 스크립트 EXE 패키징

L0: Python 없는 환경에서도 실행 가능한 독립 실행 파일 생성

이 커맨드는 PyInstaller를 사용해 Python 스크립트를 단일 EXE로 패키징한다.

## 즉시 수행할 것

아래 절차를 순서대로 실행하라. 스킬 호출 없이 직접 진행.

---

## 패키징 절차

### 1. PyInstaller 설치 확인

```powershell
pip show pyinstaller
# 없으면:
pip install pyinstaller
```

### 2. 단일 파일 EXE 빌드

```powershell
pyinstaller --onefile --name <실행파일명> <스크립트.py>
```

**추가 옵션:**
- `--noconsole` — GUI 앱이면 콘솔 창 숨김 (tkinter, PyQt 등)
- `--icon=icon.ico` — 아이콘 지정
- `--add-data "data_folder;data_folder"` — 데이터 파일 포함 (Windows: `;` 구분자)
- `--hidden-import=모듈명` — 자동 탐지 안 되는 import 수동 추가

### 3. 결과물 확인

```powershell
ls dist/
# dist/<실행파일명>.exe 생성 확인
```

### 4. 실행 테스트

```powershell
.\dist\<실행파일명>.exe
# 정상 동작 확인 후 배포
```

### 5. 클린업 (선택)

```powershell
Remove-Item -Recurse -Force build/, *.spec
```

---

## 주의사항

- **크기**: 단일 EXE는 Python 인터프리터 포함으로 30-80MB 정상
- **바이러스 오탐**: PyInstaller EXE는 일부 백신에서 오탐 — 필요시 코드 서명 적용
- **의존성**: `--onefile`은 실행 시 temp 폴더에 압축 해제 → 첫 실행이 약간 느림
- **데이터 파일 경로**: 패키징 시 `sys._MEIPASS` 경로 처리 필요

```python
import sys, os
base = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
data_path = os.path.join(base, 'data_folder')
```

---

## 배포 체크리스트

- [ ] `dist/<실행파일명>.exe` 단독 실행 테스트
- [ ] Python 미설치 환경에서 테스트 (VM 또는 다른 PC)
- [ ] 파일 크기 확인 (예상 범위: 20-100MB)
- [ ] 바이러스 스캐너 오탐 여부 확인

## 관련 커맨드

- `/careful` — EXE 배포는 비가역 행동 — 배포 전 L0 확인
- `/tdd` — 패키징 전 단위 테스트 통과 확인
