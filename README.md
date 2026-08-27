# 문서 분석 · 번역 · TTS 에이전트

## 목적

TXT 또는 DOCX 문서를 읽고 Qwen 2.5 3B가 사용자의 요청에 맞게 분석합니다.

분석 결과는 한국어·영어·일본어로 번역되며, 각 번역 결과를 Chatterbox Multilingual TTS가 WAV 파일로 생성합니다.

사용자는 Gradio 웹 화면에서 문서 업로드 → 분석 → 번역 확인 → 음성 재생까지 한 번에 수행할 수 있습니다.

## 주요 기능

- TXT 문서 읽기
- DOCX 문서 읽기
- 문서 내용 기반 AI 분석
- 사용자 지정 분석 요청 지원
- 한국어·영어·일본어 번역
- 한국어·영어·일본어 TTS 생성
- Gradio 기반 웹 UI
- Qwen 2.5 3B 로컬 추론
- Chatterbox Multilingual TTS 별도 서버 구성
- FastAPI 기반 내부 TTS API
- GPU 환경 지원

## 이 수정본이 필요한 이유

클라우드 실행 기록에서는 Python 3.13.12로 실행되었습니다.

TTS 시작 중 `PerthImplicitWatermarker`가 `None`인 오류가 발생해 FastAPI 서버가 종료됐고, 그 결과 `127.0.0.1:8001` 연결 거부가 연쇄적으로 발생했습니다.

또한 Gradio 실행 과정에서 패키지 버전 충돌과 API Schema 관련 오류가 발생하여 실행 환경을 분리할 필요가 있었습니다.

Chatterbox는 공식적으로 Python 3.11 환경에서 개발·검증된 프로젝트이므로, 수정 노트북에서는 Jupyter의 Python 3.13 환경을 직접 사용하지 않고 Miniforge를 이용해 Python 3.11 환경을 별도로 구성합니다.

앱 환경과 TTS 환경도 분리하여 라이브러리 간 충돌 가능성을 줄였습니다.

## 실행 파일

- `문서분석_번역_TTS_Linux_Jupyter_수정완료.ipynb`
  - 클라우드 환경에서 설치부터 서버 실행까지 순서대로 진행하는 Jupyter Notebook
- `app.py`
  - Gradio UI
  - TXT/DOCX 문서 읽기
  - Qwen 분석 및 번역
  - TTS API 요청
- `tts_api_server.py`
  - Chatterbox 모델을 메모리에 상주시킨 내부 FastAPI 서버
- `requirements-app.txt`
  - 문서 분석 및 Gradio 앱 환경 패키지
- `requirements-tts.txt`
  - Chatterbox TTS 서버 환경 패키지

## 구조

```text
브라우저
  │
  │ TCP 7860
  ▼
Gradio / app.py
(conda: document-app, Python 3.11)
  │
  ├─ TXT/DOCX 텍스트 추출
  │
  ├─ Qwen 2.5 3B
  │    ├─ 문서 분석
  │    └─ 한·영·일 번역
  │
  └─ HTTP 127.0.0.1:8001
             │
             ▼
      TTS API / tts_api_server.py
      (conda: document-tts, Python 3.11)
             │
             ▼
      Chatterbox Multilingual
             │
             ▼
          WAV 생성
```

TTS API는 `127.0.0.1:8001`에만 연결합니다.

외부에는 Gradio 포트 7860만 노출하며, TTS API 포트 8001은 외부에 공개하지 않습니다.

## 실행 환경

### 앱 환경

```text
Python 3.11
Gradio
Transformers
PyTorch
python-docx
Requests
```

### TTS 환경

```text
Python 3.11
Chatterbox Multilingual TTS
FastAPI
Uvicorn
PyTorch
```

## 호환성 기준

- GPU: NVIDIA Tesla T4 16GB
- 실제 확인 드라이버: 580.105.08
- CUDA 드라이버: 13.0
- Python: 3.11
- PyTorch: 2.6.0 CUDA 12.4 빌드
- LLM: `Qwen/Qwen2.5-3B-Instruct`
- TTS: `chatterbox-tts==0.1.7`

CUDA 13.0 드라이버 환경에서 CUDA 12.4용 PyTorch 빌드를 사용했습니다.

T4 한 장에서 GPU 메모리를 공유하므로 Gradio 큐의 동시 처리 수를 1로 제한했습니다.

첫 실행에는 Hugging Face 모델 다운로드 때문에 시간이 걸릴 수 있으며, 이후에는 로컬 캐시를 재사용합니다.

## 클라우드에서 실행

1. 프로젝트 파일을 클라우드 환경에 업로드합니다.
2. `문서분석_번역_TTS_Linux_Jupyter_수정완료.ipynb`를 Jupyter에서 엽니다.
3. 노트북의 셀을 위에서부터 순서대로 실행합니다.
4. Python 3.11 기반 `document-app` 환경과 `document-tts` 환경을 생성합니다.
5. TTS 서버가 정상적으로 시작되어 `TTS 준비 완료`가 출력되는지 확인합니다.
6. Gradio 서버가 정상적으로 시작되어 `Gradio 준비 완료`가 출력되는지 확인합니다.
7. NHN Cloud 보안 그룹에서 TCP 7860 포트를 허용합니다.
8. 브라우저에서 아래 주소로 접속합니다.

```text
http://<NHN-공인-IP>:7860
```

보안 그룹에서는 가능하면 **본인 IP만 TCP 7860에 접근할 수 있도록 제한하는 것을 권장합니다.**

포트 8001은 외부에 열 필요가 없습니다.

## 로컬 실행

로컬에서도 동일한 구조로 실행할 수 있습니다.

```text
document-app
    └─ app.py

document-tts
    └─ tts_api_server.py
```

먼저 TTS API 서버를 실행한 뒤 Gradio 앱을 실행합니다.

```text
TTS API
127.0.0.1:8001

Gradio
0.0.0.0:7860
```

## 문제 해결

### `PerthImplicitWatermarker` 오류

기존 Python 3.13 환경을 사용하지 말고 Python 3.11 기반 `document-tts` 환경을 사용합니다.

또한 TTS 환경에서는 `setuptools` 버전을 확인합니다.

### `pkg_resources` 관련 오류

`resemble-perth`가 `pkg_resources`를 사용하는 과정에서 최신 `setuptools`와 호환되지 않는 문제가 발생할 수 있습니다.

현재 프로젝트에서는 다음 버전을 사용합니다.

```text
setuptools==80.9.0
```

수정 노트북의 **Perth 복구** 셀을 이용하여 TTS 환경을 복구할 수 있습니다.

### TTS 준비 시간이 오래 걸리는 경우

첫 실행에서는 Chatterbox 모델 및 관련 Hugging Face 모델을 다운로드하기 때문에 시간이 오래 걸릴 수 있습니다.

이후에는 Hugging Face 캐시를 재사용합니다.

TTS 서버가 시작되지 않는 경우 다음 로그를 확인합니다.

```text
tts_server.log
```

### Gradio가 실행되지 않는 경우

Gradio 포트 `7860`이 이미 사용 중인지 확인합니다.

```bash
ss -ltnp | grep ':7860'
```

이미 실행 중인 Gradio 프로세스가 있다면 기존 프로세스를 종료한 후 다시 실행합니다.

### 외부에서 Gradio에 접속할 수 없는 경우

다음 항목을 확인합니다.

- 클라우드 공인 IP
- NHN Cloud 보안 그룹
- TCP 7860 포트 허용 여부
- Gradio 서버가 `0.0.0.0:7860`으로 실행되고 있는지 확인

TTS API의 `8001` 포트는 외부에 열지 않습니다.

### GPU 메모리가 부족한 경우

다른 GPU 프로세스를 종료한 뒤 다시 실행합니다.

계속해서 GPU 메모리가 부족한 경우 `app.py`의 LLM을 더 작은 모델로 변경할 수 있습니다.

```text
Qwen/Qwen2.5-3B-Instruct
↓
Qwen/Qwen2.5-1.5B-Instruct
```

## 보안

업로드한 문서의 내용은 로컬에서 실행되는 LLM으로 전달됩니다.

민감한 문서를 사용하는 경우 다음 설정을 권장합니다.

- 클라우드 보안 그룹에서 TCP 7860을 본인 IP로 제한
- TTS API 포트 8001 외부 공개 금지
- 공개 Gradio 공유 링크 사용 금지
- `share=True` 사용 시 민감한 문서 업로드 금지

문서 안에 포함된 명령이나 지시문은 실행 대상이 아니라 분석 대상 데이터로 취급하도록 분석 프롬프트를 구성했습니다.

## 프로젝트에서 확인한 주요 문제

이 프로젝트를 실제 클라우드 환경에서 구동하면서 다음과 같은 문제를 확인하고 수정했습니다.

- Python 3.13과 Chatterbox 관련 호환성 문제
- `PerthImplicitWatermarker` 초기화 실패
- `pkg_resources` 관련 setuptools 호환성 문제
- TTS FastAPI 서버 종료 및 `127.0.0.1:8001` 연결 거부
- Gradio와 `gradio-client` 버전 충돌
- Gradio API Schema 처리 과정에서 발생하는 오류
- 클라우드 환경에서 localhost와 외부 접속의 차이
- GPU 메모리를 고려한 앱 동시 처리 제한
- LLM과 TTS 서버의 환경 분리

단순히 코드를 작성하는 것뿐 아니라 실제 실행 과정에서 발생한 환경·의존성·서버·네트워크 문제를 확인하고 수정하는 것을 목표로 했습니다.

## 프로젝트 특징

이 프로젝트는 단순한 LLM 호출 예제가 아니라 다음과 같은 형태의 AI 애플리케이션 구조를 실험하기 위해 제작되었습니다.

```text
사용자
  ↓
웹 UI
  ↓
문서 입력
  ↓
LLM 분석
  ↓
다국어 변환
  ↓
TTS API
  ↓
음성 생성
  ↓
사용자에게 결과 제공
```

LLM과 TTS를 하나의 프로세스에 모두 넣는 대신 역할별로 분리하여 각각 독립적인 실행 환경에서 관리하도록 구성했습니다.

이를 통해 모델별 의존성 충돌을 줄이고, 향후 다른 LLM 또는 TTS 모델로 교체할 수 있는 구조를 실험했습니다.

## 제작 및 테스트

이 프로젝트는 실제 클라우드 GPU 환경에서 설치, 실행 및 디버깅 과정을 거쳐 제작되었습니다.

테스트 환경:

```text
OS: Linux
GPU: NVIDIA Tesla T4 16GB
Python: 3.11
LLM: Qwen/Qwen2.5-3B-Instruct
TTS: Chatterbox Multilingual
UI: Gradio
API: FastAPI
```

문서 분석 → 번역 → TTS 생성까지 전체 파이프라인을 실제로 연결하여 테스트했습니다.

## AI 활용

프로젝트의 초기 구현과 디버깅 과정에서 AI 코딩 도구를 활용했습니다.

다만 실제 실행 과정에서 발생한 패키지 충돌, Python 버전 문제, TTS 서버 오류, Gradio 오류, 네트워크 접속 문제 등을 직접 확인하고 환경에 맞게 수정·검증했습니다.

이 프로젝트는 AI를 이용해 코드를 생성하는 것뿐만 아니라, **생성된 코드가 실제 환경에서 동작하도록 문제를 추적하고 수정하는 과정**에 초점을 두었습니다.

사용한 AI 도구:

```text
ChatGPT / Codex
```

## 향후 개선 방향

- 더 큰 LLM 또는 최신 Qwen 모델 적용
- 문서 청크 단위 처리
- 긴 DOCX 문서 처리 성능 개선
- 번역 품질 개선
- TTS 화자 및 음성 품질 개선
- 생성된 WAV 파일 관리 기능 추가
- PDF 지원
- 음성 길이에 따른 자동 텍스트 분할
- LLM과 TTS의 GPU 메모리 관리 최적화
- 에이전트 기반 작업 분배 구조로 확장

## 라이선스 및 모델

본 프로젝트에서 사용하는 모델과 라이브러리는 각각의 원본 라이선스를 따릅니다.

- Qwen: `Qwen/Qwen2.5-3B-Instruct`
- Chatterbox: `chatterbox-tts`
- Gradio
- FastAPI
- PyTorch
- Hugging Face Transformers

각 모델 및 라이브러리를 실제 배포 또는 상업적 용도로 사용하는 경우 해당 프로젝트의 최신 라이선스와 이용 조건을 확인해야 합니다.

## 제작

해당 프로젝트는 ChatGPT / Codex 기반 AI 코딩 지원을 활용하여 제작되었습니다.

실제 구동을 위해서는 GPU가 포함된 클라우드 환경 또는 충분한 GPU 자원을 가진 로컬 환경이 필요합니다.
