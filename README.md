# 문서 분석 · 번역 · TTS 에이전트

## 목적

TXT 또는 DOCX 문서를 읽고 Qwen 2.5 3B가 요청에 맞게 분석합니다. 분석 결과는 한국어·영어·일본어로 번역되며, 각 번역 결과를 Chatterbox Multilingual TTS가 WAV 파일로 생성합니다. 사용자는 Gradio 웹 화면에서 업로드·분석·번역 확인·음성 재생을 한 번에 수행합니다.

## 이 수정본이 필요한 이유

클라우드 실행 기록에서는 Python 3.13.12로 실행되었습니다. TTS 시작 중 `PerthImplicitWatermarker`가 `None`인 오류가 발생해 FastAPI 서버가 종료됐고, 그 결과 `127.0.0.1:8001` 연결 거부가 연쇄적으로 발생했습니다. 또한 Gradio 시작 셀은 `os`를 가져오지 않아 `NameError`가 발생했습니다.

Chatterbox는 공식 문서에서 Python 3.11/Debian 11 환경에서 개발·검증됐다고 안내합니다. 따라서 수정 노트북은 Jupyter의 Python 3.13을 사용하지 않고, Miniforge로 Python 3.11 환경을 두 개 만듭니다. Chatterbox와 앱 라이브러리를 격리해 버전 충돌도 막습니다.

## 실행 파일

- `문서분석_번역_TTS_Linux_Jupyter_수정완료.ipynb`: 클라우드에서 순서대로 실행할 노트북
- `app.py`: Gradio UI, 문서 읽기, Qwen 분석·번역, TTS 요청
- `tts_api_server.py`: Chatterbox 모델을 메모리에 상주시킨 내부 FastAPI 서버

## 구조

```text
브라우저
  │ TCP 7860
  ▼
Gradio / app.py  (conda: document-app, Python 3.11)
  ├─ TXT/DOCX 텍스트 추출
  ├─ Qwen 2.5 3B: 분석 및 한·영·일 번역
  └─ HTTP 127.0.0.1:8001
       ▼
    TTS API / tts_api_server.py  (conda: document-tts, Python 3.11)
       └─ Chatterbox Multilingual: WAV 생성
```

TTS 포트는 `127.0.0.1`에만 연결합니다. 외부에는 Gradio 포트 7860만 열어, TTS API가 직접 노출되지 않게 했습니다.

## 클라우드에서 할 일

1. 프로젝트 파일과 수정완료 노트북을 같은 폴더(예: `/home/ubuntu`)에 둡니다.
2. NHN 보안 그룹에서 **본인 IP만** TCP 7860을 허용합니다. 포트 8001은 열지 않습니다.
3. 노트북을 열고 위부터 아래로 실행합니다. 환경 설치는 최초 한 번만 필요합니다.
4. `TTS 준비 완료`과 `Gradio 준비 완료` 메시지를 확인합니다.
5. `http://<NHN-공인-IP>:7860`으로 접속합니다.

## 호환성 기준

- GPU: NVIDIA Tesla T4 16GB
- 실제 확인 드라이버: 580.105.08 / CUDA 13.0
- 실행 환경: Python 3.11 고정
- PyTorch: 2.6.0 CUDA 12.4 빌드. CUDA 13 드라이버는 CUDA 12.4 빌드를 하위 호환으로 실행합니다.
- Qwen: `Qwen/Qwen2.5-3B-Instruct`
- Chatterbox: `chatterbox-tts==0.1.7`

T4 한 장에서는 분석 요청을 동시에 하나만 처리하도록 Gradio 큐를 제한했습니다. 첫 실행에는 Qwen과 Chatterbox 모델 다운로드 때문에 시간이 걸리지만, 이후에는 Hugging Face 캐시를 재사용합니다.

## 문제 해결

- `PerthImplicitWatermarker` 오류: 기존 Python 3.13 가상환경을 사용하지 말고 수정 노트북의 Python 3.11 환경 생성·설치 셀부터 다시 실행합니다.
- TTS 준비 시간이 길다: TTS 모델 첫 다운로드는 수 분 걸립니다. 수정본은 최대 10분 대기하고, 실패 시 `tts_server.log` 마지막 내용을 표시합니다.
- 외부에서 화면에 접속할 수 없다: 보안 그룹의 TCP 7860과 공인 IP를 확인합니다. 8001을 외부에 열 필요는 없습니다.
- GPU 메모리 부족: 다른 GPU 프로세스를 종료하고, 계속 부족하면 `app.py`의 모델을 `Qwen/Qwen2.5-1.5B-Instruct`로 낮춥니다.

## 보안

업로드 문서 내용이 로컬 모델에 전달됩니다. 민감 문서에는 보안 그룹을 본인 IP로 제한하고, 공개 Gradio 주소 또는 `share=True`를 사용하지 마세요. 문서 속 명령은 데이터로만 취급하도록 분석 프롬프트를 작성했습니다.
## Perth / setuptools 필수 고정

`resemble-perth` 1.0.1은 내부적으로 `pkg_resources`를 사용합니다. `setuptools` 81 이상에서는 이 모듈이 제거되어 Perth가 오류를 숨긴 채 `PerthImplicitWatermarker = None`으로 설정됩니다. 따라서 TTS 환경에서는 반드시 `setuptools==80.9.0`을 사용해야 합니다. 수정 노트북의 **Perth 복구** 셀을 실행하면 이미 만든 환경도 바로 복구됩니다.

해당 파일은 chatgpt codex를 이용하여 만들어졌습니다.
