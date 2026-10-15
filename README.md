# dada-ux 마켓플레이스

다다 UX팀 기획자를 위한 Claude 플러그인 `ux-team`을 담은 저장소입니다.
Chat · Cowork · Code 탭에서 같은 스킬을 씁니다.

## 구조

```
.claude-plugin/marketplace.json   마켓플레이스 정의 (dada-ux)
plugins/ux-team/                  플러그인
  .claude-plugin/plugin.json      버전 필드 없음: 커밋마다 갱신이 전파됨
  skills/<스킬>/SKILL.md          스킬 11개
  skills/<스킬>/references/_shared/  shared/에서 복사된 공유 사본 (직접 고치지 않음)
shared/                           여러 스킬이 쓰는 원본 (팀 지침 · 교차 지점 · 토큰 · 글쓰기 · 화면 분기)
scripts/skills.py                 sync(공유 사본 복사) · check(규칙 점검)
docs/                             명세 · 트리거 지도 · 작성 규칙 · eval
```

## 작업 명령

```
python3 scripts/skills.py sync    # shared/ 원본을 각 스킬로 복사
python3 scripts/skills.py check   # frontmatter · 리드 전용 흔적 · 공유 사본 · 트리거 지도 일치 점검
claude plugin validate .          # 마켓플레이스와 플러그인 형식 점검
```

## 설치 (팀원)

이 저장소(`lee-changwook/ux-team-marketplace`)는 공개라 초대 없이 추가할 수 있습니다.

- Chat · Cowork: Claude 앱의 Customize › Plugins에서 이 저장소를 마켓플레이스로 추가합니다.
- Code 탭:

```
/plugin install ux-team --marketplace lee-changwook/ux-team-marketplace
```

설치한 뒤 `/hello-ux-team`을 실행합니다.

`tikita-policy`는 준비 중입니다.
정책 위키는 공개 저장소에 담지 않고, 회사 조직의 위키 저장소가 생기면 거기서 읽도록 바꿉니다.

하네스 안내: https://claude.ai/artifact/A39pdxytvgJuhiac7Vw3ba
