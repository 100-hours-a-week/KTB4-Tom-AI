# 커뮤니티 서비스 백엔드 (FastAPI + SQLAlchemy + Ollama)

FastAPI로 구현한 커뮤니티 게시판 백엔드입니다. 게시글과 댓글의 CRUD를 제공하고, 로컬 LLM(Ollama)을 호출해 본문/댓글 요약 기능을 제공합니다.

## 프로젝트 구조

```
02/
├── main.py                       # FastAPI 앱 생성, 라우터 등록, lifespan
├── database.py                   # 엔진, 세션, Base, get_session
├── models/                       # SQLAlchemy DB 모델
│   ├── post_model.py
│   ├── comment_model.py
│   └── llm_model.py              # LLM 호출 헬퍼
├── schemas/                      # Pydantic 입출력 스키마
│   ├── post_schema.py
│   ├── comment_schema.py
│   └── llm_schema.py
├── controllers/                  # 비즈니스 로직
│   ├── post_controller.py
│   ├── comment_controller.py
│   └── llm_controller.py
├── routers/                      # HTTP 라우팅
│   ├── post_router.py
│   ├── comment_router.py
│   └── llm_router.py
└── community.db                  # SQLite 데이터 파일
```

## API 명세

### 게시글 (Post)

| 메서드 | 경로 | 설명 |
|---|---|---|
| `POST` | `/posts` | 게시글 생성 |
| `GET` | `/posts` | 전체 게시글 조회 |
| `GET` | `/posts/{post_id}` | 단일 게시글 조회 |
| `PUT` | `/posts/{post_id}` | 게시글 수정 |
| `DELETE` | `/posts/{post_id}` | 게시글 삭제 (댓글도 함께 cascade 삭제) |

### 댓글 (Comment)

| 메서드 | 경로 | 설명 |
|---|---|---|
| `POST` | `/posts/{post_id}/comments` | 댓글 생성 |
| `GET` | `/posts/{post_id}/comments` | 게시글의 모든 댓글 조회 |
| `GET` | `/posts/{post_id}/comments/{comment_id}` | 단일 댓글 조회 |
| `PUT` | `/posts/{post_id}/comments/{comment_id}` | 댓글 수정 |
| `DELETE` | `/posts/{post_id}/comments/{comment_id}` | 댓글 삭제 |

### LLM 요약

| 메서드 | 경로 | 설명 |
|---|---|---|
| `GET` | `/posts/{post_id}/summary` | 게시글 요약 |
| `GET` | `/posts/{post_id}/comments/{comment_id}/summary` | 댓글 요약 |

## 단계별 진행 과정

과제는 다음 4단계로 점진적으로 확장하며 진행했습니다.

1단계 — 메모리 기반 REST API

2단계 — LLM 연동 (Ollama)

3단계 — 데이터베이스 적용 (SQLAlchemy 2.x + SQLite)

4단계 — 구조 개선 (Router - Controller - Model)

## 회고

간단한 게시판 기능을 가진 서비스를 만드는 것이라 생각했지만 막상 시작하려고 보니 어떻게 시작해야될지 감이 잡히지 않았다.
한 단계씩 구현을 따라가면서 모르는 개념들이 많이 나와서 이 코드가 어떤 코드이고 무슨 기능을 하는지 이해하는데 오랜 시간이 걸린 것 같다.
이번 위클리 챌린지를 진행하면서는 다른 팀원분들의 배움일기나 코드를 많이 참고하며 완성할 수 있었다.
완전히 무에서 유를 생성해내기엔 많이 부족하다고 느껴서 다른 분들의 코드를 참고하며 코드가 어떤 형식으로 연결되는지 이해하려고 했고,
AI에게 어떤 기능의 한 부분만 코드 예시를 알려달라고 하고 다른 기능들은 직접 구현한 후에 제대로 짰는지 다시 물어보는 식으로 AI를 사용했다.
이렇게 서비스를 완성해낼 수 있었지만 약간의 찝찝함과 내가 전부 이해하며 코드를 작성하지는 못했다는 아쉬움이 남았다.
그래서 후에 다시 이 서비스의 코드를 공부하고 구현하며 내 것으로 만드려고 한다.