---
1. 논문/시스템별 질문 템플릿
아래 블록을 논문마다 하나씩 복사해서 쓴다.
```md
# [논문/시스템 이름]

## 1) 내가 이해한 배경
- 이 논문/시스템이 풀려는 문제:
- 왜 내가 이걸 보고 있는지:
- 내가 특히 헷갈리는 부분:

## 2) 내가 원하는 답변 스타일
- 직관 위주 / 수식 위주 / 구현 위주 중 무엇이 중요한지:
- 수식 설명 필요 여부:
- 의사코드 필요 여부:
- 예시 필요 여부:

## 3) 핵심 질문
1.
2.
3.

## 4) 내 현재 추측
- 추측 1:
- 추측 2:
- 추측 3:

## 5) Claude에게 요구할 것
- 내 추측이 맞는지 틀린지 명확히 판단해줘.
- 논문 표현 그대로의 의미와, 실제 구현 관점의 의미를 분리해서 설명해줘.
- online / evolution / memory / verifier 같은 단어가 나오면 추상적으로 말하지 말고, 실제로 무엇이 업데이트되고 무엇이 선택되는지 써줘.
- 필요하면 간단한 toy example로 설명해줘.

## 6) 답변 공간
### Q1
- 한 줄 요약:
- 정의:
- 왜 필요한가:
- 논문 내 역할:
- 예시:
- 내 추측 검증:
- 헷갈리는 포인트:

### Q2
- 한 줄 요약:
- 정의:
- 왜 필요한가:
- 논문 내 역할:
- 예시:
- 내 추측 검증:
- 헷갈리는 포인트:

### Q3
- 한 줄 요약:
- 정의:
- 왜 필요한가:
- 논문 내 역할:
- 예시:
- 내 추측 검증:
- 헷갈리는 포인트:

## 7) 마지막 정리
- 이 논문의 핵심 아이디어:
- 실제 구현 포인트:
- 후속 질문:
```
---

---
[Paper 1] AlphaEvolve
```md
# AlphaEvolve

## 1) 내가 이해한 배경
- 이 논문/시스템은 LLM과 evolutionary search를 결합해서 프로그램/알고리즘을 개선하는 쪽으로 이해하고 있다.
- 나는 특히 automated metric이 왜 한계가 되는지, 그리고 evolution 단계의 population 운영 방식이 궁금하다.

## 2) 내가 원하는 답변 스타일
- 개념 + 알고리즘 흐름 위주
- 수식이 있으면 간단히 포함
- 예시 필요

## 3) 핵심 질문
1. "Automated Metric으로 인한 한계"가 존재한다는 게 정확히 무슨 의미인가?
2. Evolution 단계에서 MAP가 정확히 무엇을 뜻하는가?
3. Island-based population model은 무엇이고, 왜 쓰는가?

## 4) 내 현재 추측
- automated metric의 한계는, 사람이 보기엔 좋은 해가 자동 평가 점수로는 잘 안 잡히는 문제를 말하는 것 같다.
- MAP는 단순히 최고 점수 해를 고르는 방식일 수도 있고, posterior 관점의 best candidate일 수도 있어서 헷갈린다.
- island-based population model은 population을 여러 그룹으로 나눠 diversity를 유지하는 장치 같긴 하다.

## 5) Claude에게 요구할 것
- MAP가 이 논문 맥락에서 정확히 무엇인지 일반 용례와 구분해서 설명해줘.
- automated metric limitation이 실제로 어떤 실패를 만드는지 예시를 들어줘.
- island model에서 selection / migration / mutation이 어떻게 돌아가는지 단계별로 설명해줘.

## 6) 답변 공간

### Q1 Automated Metric limitation
- 한 줄 요약: AlphaEvolve는 솔루션의 품질을 자동으로 수치화할 수 있는 문제에만 적용 가능하며, 그게 불가능한 도메인에서는 근본적으로 작동하지 않는다.
- 정의: Automated metric이란 AlphaEvolve의 `evaluate(eval_inputs) -> dict[str, float]` 함수처럼, 생성된 코드/알고리즘을 실행했을 때 자동으로 점수(scalar)를 반환하는 평가 메커니즘. Section 2.1에서 "AlphaEvolve tackles problems with machine-gradeable solutions"로 명시.
- 왜 필요한가: 진화 루프가 돌아가려면 매 iteration마다 수천~수만 개의 후보 프로그램을 자동으로 점수 매길 수 있어야 한다. 단일 솔루션 평가에 최대 100 compute-hours까지 쓸 수 있으나 이는 병렬 자동화 전제.
- 논문 내 역할: Section 6에서 "main limitation"으로 명시: "it handles problems for which it is possible to devise an automated evaluator."
- 예시: (적용 가능) 행렬 곱셈 rank, 키싱 넘버, 데이터센터 스케줄링 효율, TPU 커널 실행 시간. (적용 불가) 신약 후보 독성·효과(세포 실험 필요), 법률 문서 타당성, 소설·시의 문학적 품질, 물리적 재료 특성, 증명의 우아함.
- 내 추측 검증: **부분적으로 맞다.** "사람이 보기엔 좋은 해가 자동 평가로 잘 안 잡히는 문제"라는 측면도 있으나, 핵심 한계는 자동 평가 함수 자체가 존재하지 않거나 만들 수 없는 도메인에서 AlphaEvolve 자체가 작동하지 않는다는 것이다.
- 헷갈리는 포인트: LLM-provided evaluation이 있으니 "LLM이 점수를 주면 되지 않냐"고 생각할 수 있으나, 논문은 이것이 현재 주 최적화 대상이 아님을 명시.

### Q2 MAP-Elites
- 한 줄 요약: MAP-Elites는 Maximum A Posteriori와 전혀 무관하며, 다차원 행동 공간을 격자로 나눠 각 셀에서 최고 품질의 해 하나씩만 유지하는 Quality-Diversity 알고리즘이다.
- 정의: MAP-Elites(Multi-dimensional Archive of Phenotypic Elites, Mouret & Clune 2015)는 (1) "행동 특성" 공간을 다차원 격자로 이산화, (2) 각 셀에 최고 점수 솔루션 1개만 저장, (3) 새 솔루션이 해당 셀의 기존보다 높을 때만 교체. Bayesian 추론과 무관.
- 왜 필요한가: 최고 점수 해 하나만 추적하면 조기 수렴. MAP-Elites는 "서로 다른 특성의 다수 고품질 해"를 동시 유지하여 LLM이 더 넓은 아이디어 공간을 탐색하도록 돕는다.
- 논문 내 역할: Program Database(Section 2.5)의 핵심. "maintain diversity to encourage exploration"이 목적.
- 예시: 수식 최적화에서 behavioral descriptor를 "수식 길이"×"연산자 종류 수"로 정의하면 3×3=9 셀. "짧고 단순한 0.7점 해"와 "길고 복잡한 0.9점 해"가 공존. 프롬프트에 두 해를 모두 참조 가능.
- 내 추측 검증: **틀렸다(MAP 해석).** "MAP가 Maximum A Posteriori일 수 있다"는 완전히 틀렸다. "최고 점수 해를 고르는 방식"은 절반 맞다 — 각 셀 안에서는 최고 점수이지만, 전체에는 다양한 해가 공존.
- 헷갈리는 포인트: 논문이 MAP-Elites의 behavioral descriptor가 무엇인지 구체적으로 공개하지 않음. "island model과 MAP-Elites를 조합한 알고리즘에서 영감"이라고만 기술.

### Q3 Island-based population model
- 한 줄 요약: 전체 population을 여러 독립 island로 나눠 각각 독자 진화시키다가 주기적으로 migration/reset하여 다양성을 구조적으로 보장하는 모델.
- 정의: 분산 유전 알고리즘의 일종. 여러 "island"를 동시 운영하며 독자적 진화 압력을 받게 하고, 주기적 migration(우수 개체 전송)과 reset(재시작)을 수행.
- 왜 필요한가: 단일 population은 빠르게 local optimum에 수렴. Island 모델은 격리 기간 + migration + reset으로 다양성을 동적 주입.
- 논문 내 역할: Program Database(Section 2.5)에서 MAP-Elites와 함께 탐색-활용 균형 담당. 비동기 분산 파이프라인과 구조적 시너지.
- 예시: (1) 초기화: 5개 island에 초기 프로그램 독립 복사. (2) 독립 진화: 각 island에서 별도 진화 루프. (3) Migration: 주기적으로 각 island 최고 해를 다른 island로 복사. (4) Reset: 정체된 island 재시작. (5) 수렴: 전체 island 최고 점수 모니터링.
- 내 추측 검증: **대체로 맞다.** "population을 여러 그룹으로 나눠 diversity 유지"는 정확. 보완: migration과 reset이라는 능동적 메커니즘으로 다양성이 동적 주입됨.
- 헷갈리는 포인트: Island model과 MAP-Elites가 Program Database에서 어떻게 함께 작동하는지 논문이 구체적으로 분리 설명하지 않음.

## 7) 마지막 정리
- 이 논문의 핵심 아이디어: LLM(아이디어 생성) + evaluator(진실 판별) + 진화(둘을 연결)로 수십 년 미해결 수학 문제와 구글 인프라 최적화에서 실질적 돌파구.
- 실제 구현 포인트: (1) EVOLVE-BLOCK 마커로 기존 코드에 최소 침습적 통합, (2) evaluate 함수 설계가 성패 좌우, (3) Flash+Pro 앙상블로 throughput과 품질 동시 확보, (4) Evaluation cascade로 불량 조기 필터링, (5) 복수 metric 동시 최적화가 더 나은 탐색 다양성 제공.
- 후속 질문: MAP-Elites의 behavioral descriptor 구체 정의? Island 수와 migration 주기의 하이퍼파라미터 민감도? LLM-provided evaluation과 automated metric 가중치 조율?
```
---
[Paper 2] Automatic Programming via Large Language Models With Population Self-Evolution for Dynamic Fuzzy Job Shop Scheduling Problem
```md
# Automatic Programming via Large Language Models With Population Self-Evolution for Dynamic Fuzzy Job Shop Scheduling Problem

## 1) 내가 이해한 배경
- 이 논문은 dynamic fuzzy job shop scheduling에서 LLM이 heuristic/program을 만들고 population self-evolution으로 개선하는 것으로 이해하고 있다.
- 나는 online application의 의미와 feature 설계의 의미가 특히 궁금하다.

## 2) 내가 원하는 답변 스타일
- 구현 관점 + 직관 위주
- 수식 설명 필요
- online 단계는 실제 배포/실행 관점에서 설명 필요

## 3) 핵심 질문
1. Online application이 정확히 무엇을 하는 단계인가?
2. "알고리즘을 실시간 배포한다"는 것이 이 논문에서 정확히 무슨 의미인가?
3. P'/P - 1의 EMA는 어디에 넣는 것인가? 입력 feature인가, priority rule 일부인가, state summary인가?
4. realtime deviation trend를 넣는 게 어떤 의미가 있는가?
5. 이 feature가 의미 있으려면, realtime deviation을 고려하지 않으면 성능 붕괴가 일어나거나 fuzzy info에 자기상관이 있어야 하는가?

## 4) 내 현재 추측
- online application은 offline에서 만든 heuristic/program을 실제 동적 환경에서 계속 적용하는 단계 같긴 하다.
- 실시간 배포라는 말은 모델 자체를 재학습하는 게 아니라, 현재 상태를 받아 즉시 dispatching rule/priority score를 계산하는 의미일 수도 있다.
- P'/P - 1의 EMA는 최근 진행률 변화나 deviation 변화를 smoothing해서 state input으로 넣는 것 같다.
- realtime deviation trend는 시스템이 지금 악화되는 중인지 개선되는 중인지의 방향성을 알려주는 것 같다.
- 이게 의미 있으려면 deviation process에 어느 정도 persistence나 autocorrelation이 있어야 할 것 같다.

## 5) Claude에게 요구할 것
- online phase에서 시간 t마다 정확히 무엇이 입력되고 무엇이 출력되는지 단계별로 써줘.
- P'/P - 1에서 P와 P'가 정확히 무엇인지 논문 정의 기준으로 설명해줘.
- EMA가 어느 블록에 들어가며, decision rule에 어떻게 영향을 미치는지 써줘.
- realtime deviation trend가 유효하려면 어떤 데이터 generating process를 암묵적으로 가정하는지도 평가해줘.
- 내 추측이 맞는지 틀린지 항목별로 판단해줘.

## 6) 답변 공간

### Q1 Online application
- 한 줄 요약: Self-evolution(offline)에서 만들어진 최고 성능 HDR을 실제 동적 스케줄링 환경에 바로 적용하는 배포 단계.
- 정의: Section 3.4의 두 번째 단계. 20개 훈련 케이스와 최대 20세대 진화를 거쳐 생성된 best HDR(Python 함수)을 실제 DFJSSP 환경에 적용. "단 한 번의 추론 패스"로 적용.
- 왜 필요한가: 매 스케줄링 결정 시마다 LLM을 수십 분씩 실행하는 병목 해결. 진화는 offline에서 한 번만, 현장에서는 HDR 코드만 실행. 100 jobs × 20 machines 기준 약 40초.
- 논문 내 역할: SeEvo의 실용성 보장. "This two-stage design directly addresses the timeliness bottleneck."
- 단계별 흐름: (1) Offline에서 LLM 진화 → best HDR 선출 (2) HDR 코드를 스케줄링 시스템에 탑재 (3) Machine 유휴 시 job pool에서 feature 수집 (4) EMA 업데이트 (5) HDR 함수 호출 → priority score 계산 (6) 최고 priority job을 machine에 배정 (7) 반복. LLM은 전혀 호출되지 않음.
- 내 추측 검증: **맞다.**
- 헷갈리는 포인트: "online"은 인터넷/LLM API가 아니라 "실시간 운영 환경".

### Q2 Real-time deployment meaning
- 한 줄 요약: 이미 완성된 HDR Python 함수를 매 dispatching 결정 시점마다 즉시 실행하는 것이며, 재학습이나 LLM 호출 없음.
- 정의: HDR 코드가 실시간 스케줄링 이벤트에 반응하여 즉각 실행되는 방식.
- 왜 필요한가: DFJSSP의 동적 특성으로 dispatching 결정이 수시 발생. 지연은 makespan 악화.
- 논문 내 역할: "Applies HDRs to real-world scenarios in a single inference pass."
- 예시: 100 jobs × 20 machines에서 GPT-4.1-mini HDR은 전체 시뮬레이션 약 42초. 실제 dispatching 한 번은 밀리초 단위.
- 내 추측 검증: **맞다.**
- 헷갈리는 포인트: DRL은 neural network 추론이 real-time, SeEvo는 Python 함수 실행이 real-time.

### Q3 P'/P - 1 EMA
- 한 줄 요약: 작업별로 계획 대비 실제 처리 시간의 상대적 편차를 지수이동평균으로 누적한 8번째 입력 feature `ema`.
- 정의: Section 3.3 Equation 1: phi_ij = kappa * delta_ij + (1-kappa) * phi_{i-1,j}, where delta_ij = (p'_ij / p_ij) - 1.
- 변수 의미: p_ij = 계획 처리 시간(fuzzy 기댓값), p'_ij = 실제 처리 시간(gamma 노이즈 적용), delta_ij = 상대적 편차(양수=예상보다 느림), kappa=0.2(최근 20%, 과거 80%), phi_ij = 갱신된 EMA 값.
- 어디에 들어가는가: Section 3.2 Table 1의 8개 feature 중 6번째 `ema`. HDR 함수의 (pt, wkr, rm, so, twk, **ema**, dd, et) 중 ema가 phi_ij.
- 왜 필요한가: Teacher-student 패러다임의 핵심. Student(HDR)가 접근 불가능한 실제 처리 시간 정보를 과거 편차 이력으로 간접 추론. Ablation에서 ema 없으면 성능 저하 확인.
- 내 추측 검증: **부분적으로 맞다.** 'smoothing해서 input으로 넣는 것'은 맞으나, '진행률 변화'가 아니라 '처리 시간의 상대적 편차(실제/계획 - 1)'를 smoothing하는 것.
- 헷갈리는 포인트: phi_ij를 그대로 ema로 넘기는지, pt에 보정하여 넘기는지 논문에서 명확하지 않음. GitHub 코드 확인 필요.

### Q4 Realtime deviation trend
- 한 줄 요약: EMA(phi_ij)는 각 job의 operation별 편차 방향성(계획보다 지속적으로 느린지/빠른지)을 나타내며, HDR의 우선순위 결정에 반영.
- 정의: phi_ij > 0이면 악화 경향, < 0이면 개선 경향. kappa=0.2이므로 지속적 경향을 더 강하게 반영.
- 왜 필요한가: 특정 job의 재료 특성이나 공정 난이도가 일관된 편차를 만들면 미래 예측에 유용.
- 어떤 상황에서 유효한가: (1) 편차에 persistence 있을 때 (2) pure random noise라도 EMA 자체가 평균 편차 수준의 통계적 요약 정보 제공. Ablation으로 실효성 경험적 증명.
- 내 추측 검증: **맞다.** 단, 시스템 전체가 아닌 각 job 개별의 편차 방향성. 자기상관이 없어도 EMA smoothing 자체가 유용한 통계적 요약 제공(gamma(1.0, 0.10)은 memoryless인데도 효과적).
- 헷갈리는 포인트: gamma(shape=1.0, scale=0.10)은 지수 분포와 동일하여 이론적으로 operation 간 자기상관 없음. 그럼에도 ema가 효과적인 것은 noise를 줄인 평균 편차 수준 추정치 역할.

## 7) 마지막 정리
- 이 논문의 핵심 아이디어: (1) offline 진화와 online 실행 분리로 실용성 확보, (2) Teacher-student로 ema feature를 통한 fuzzy 정보 간접 학습, (3) Self-evolution reflection으로 탐색-활용 강화.
- 실제 구현 포인트: EMA는 job별 독립 업데이트(kappa=0.2), HDR 입력은 8개 feature, generation=20/population=20/mutation rate=0.9/temperature=1.0이 최적.
- 후속 질문: phi_ij를 pt에 mapped back하는 정확한 수식? kappa=0.2 고정 근거? gamma noise가 job 내 독립인지 correlated인지?
```
---
[Paper 3] Mathematical discoveries from program search with large language models
```md
# Mathematical discoveries from program search with large language models

## 1) 내가 이해한 배경
- 이 논문은 LLM 기반 program search를 통해 수학적 발견이나 conjecture/algorithm을 탐색하는 계열로 이해하고 있다.
- 나는 전체 파이프라인과 평가 방식, 그리고 실제로 무엇이 "discovery"로 인정되는지가 궁금하다.

## 2) 내가 원하는 답변 스타일
- 개념 + 사례 + 파이프라인 위주
- 가능하면 toy example 포함

## 3) 핵심 질문
1. 이 논문에서 program search는 정확히 어떤 객체를 탐색하는가?
2. 단순히 높은 점수의 프로그램을 찾는 것과 "mathematical discovery"의 차이는 무엇인가?
3. evaluation / verifier / human inspection은 어떻게 역할이 나뉘는가?
4. 결과물이 conjecture, heuristic, proof aid 중 무엇에 가까운가?

## 4) 내 현재 추측
- 그냥 점수 최적화만으로는 discovery라고 부르기 어려워서, 해석 가능성이나 일반화 검증이 따로 있어야 할 것 같다.
- verifier와 human inspection이 둘 다 필요한 이유는 자동 평가만으로는 수학적 의미를 다 보장 못하기 때문인 것 같다.

## 5) Claude에게 요구할 것
- pipeline을 처음부터 끝까지 단계별로 설명해줘.
- search object, scoring, filtering, final validation을 구분해서 설명해줘.
- 무엇이 novelty로 인정되는지 말해줘.
- 내 추측이 맞는지 평가해줘.

## 6) 답변 공간

### Q1 Search object
- 한 줄 요약: FunSearch가 탐색하는 대상은 해 자체가 아니라, 해를 생성하는 Python 프로그램(함수)이다.
- 정의: "function space" 탐색. cap set에서는 `priority(element, n) -> float`, bin packing에서는 `heuristic(item, bins) -> np.ndarray`를 진화시킴.
- 왜 필요한가: 해를 직접 탐색하면 탐색 공간이 천문학적. 프로그램은 더 간결하고 해석 가능.
- 논문 내 역할: Section 2.2. 사용자가 evaluate 함수와 초기 함수를 제공, LLM이 초기 함수만 변이·개선.
- 예시: [Cap set] priority 함수가 각 벡터에 점수 → solve가 greedy로 cap set 구성 → evaluate가 크기 반환. 초기값은 `return 0.0`. [Bin packing] heuristic이 각 bin에 점수 → argmax로 선택 → evaluate가 bin 수의 음수 반환.
- 내 추측 검증: (별도 추측 없음) "cap set 자체를 직접 탐색한다"는 오해는 틀림. priority 함수 코드가 search object.
- 헷갈리는 포인트: solve(고정 skeleton)와 priority(진화 대상)를 혼동하기 쉬움. evaluate는 채점자이지 탐색 대상이 아님.

### Q2 Discovery meaning
- 한 줄 요약: "Discovery" = 기존 best-known result를 능가하는 새로운 수학적 구성 발견.
- 정의: "Surpassing state-of-the-art results on established open problems provides a clear indication that the discoveries are truly new."
- 왜 단순 optimization과 다른가: discovery에는 (1) 기존 best-known 초과 + (2) 새로운 아이디어/구조가 모두 필요. 단순 최적화는 (1)만.
- 검증 방식: (a) evaluate로 수치 검증, (b) 연구자가 코드 분석하여 explicit construction 도출, (c) 전문가가 수학적 구조와 연결 확인.
- 내 추측 검증: **대체로 맞다.** 점수 최적화는 필요조건이지 충분조건이 아님.
- 헷갈리는 포인트: Bin packing에서의 "discovery"는 수학적 discovery가 아니라 "new algorithm discovery"로 기준이 다름.

### Q3 Validation pipeline
- 한 줄 요약: 3단계: (a) 프로그램 실행 시 자동 필터링, (b) evaluate의 수치 점수, (c) 인간 전문가의 코드 분석.
- 단계별 설명: 1단계(실행 시간/메모리/출력 형식 자동 검증) → 2단계(evaluate로 점수 산출, island DB에 저장) → 3단계(인간이 코드에서 수학적 패턴 발견, feedback loop).
- verifier 역할: evaluate 함수 자체가 verifier. 유효성 검사(is_capset) + 품질 점수화(크기)의 결합체.
- human role: 사후 개입. (1) 코드에서 패턴 추출 → 명시적 구성, (2) 발견된 symmetry로 탐색 공간 좁혀 재실행.
- 내 추측 검증: **정확하다.**
- 헷갈리는 포인트: None 반환은 프로그램 폐기이지 수학적 반증이 아님.

### Q4 결과물의 성격
- Cap set: explicit construction (증명 가능한 하한 증거)
- Admissible set: proof aid (인간이 추가 분석으로 증명 완성)
- Bin packing: 순수 heuristic

## 7) 마지막 정리
- 이 논문의 핵심 아이디어: LLM(창의적 변이) + evaluate(hallucination 필터) + 진화, 프로그램을 탐색하여 수학적 발견.
- 실제 구현 포인트: evaluate 설계가 핵심, skeleton 분리, k=2 best-shot prompting, 15 samplers + 150 evaluators, 4시간마다 하위 50% island 초기화. n=8 cap set 성공률 2.9%.
- 후속 질문: evaluate 자동 생성 가능성? skeleton 한계? 학습 데이터와의 관계?
```
---
[Paper 4] Evolution of Heuristics
```md
# Evolution of Heuristics

## 1) 내가 이해한 배경
- 이 논문/아이디어는 heuristic을 자연어/코드 형태로 표현하고, 이를 변이/개선하면서 더 나은 heuristic을 찾는 접근으로 이해하고 있다.
- 나는 representation, selection, mutation loop, problem set 평가 의미가 궁금하다.

## 2) 내가 원하는 답변 스타일
- 알고리즘 흐름 위주
- selection / mutation / evaluation 분리 설명
- 가능하면 pseudo-code 포함

## 3) 핵심 질문
1. 자연어 묘사와 implement code를 둘 다 생성시킬 필요가 있는가?
2. candidate heuristic pool에서 mutate / operation을 진행할 때 selection은 어떻게 하는가?
3. mutate하고 나서 반복하는 구조인가? 전체 루프를 설명해줘.
4. set of problem에 적용한다는 것은 무슨 의미인가?

## 4) 내 현재 추측
- 자연어 묘사는 LLM이 reasoning/variation하기 쉽게 하고, 코드는 실제 실행 평가를 위해 필요한 것 같다.
- selection은 아마 validation set에서 성능이 좋은 heuristic을 우선 남기는 방식일 것 같다.
- 단일 problem이 아니라 problem set에 적용하는 건 특정 instance overfitting을 막기 위한 것 같다.

## 5) Claude에게 요구할 것
- representation을 왜 두 층(설명/코드)으로 두는지 설명해줘.
- selection 기준이 score only인지 diversity까지 보는지 설명해줘.
- mutation-evaluation-selection 반복 루프를 의사코드 수준으로 써줘.
- set of problem 평가가 generalization 관점에서 왜 중요한지 말해줘.
- 내 추측을 맞다/틀리다로 평가해줘.

## 6) 답변 공간

### Q1 Natural language + code
- 한 줄 요약: EoH는 각 heuristic을 자연어 thought + Python code 두 가지로 동시 표현하고 함께 진화시키는 것이 핵심.
- 정의: 각 heuristic hi = (자연어 description, Python code, fitness). Section 3.3.
- 왜 둘 다 필요한가: thought는 LLM의 in-context learning과 reasoning에 사용, code는 실행 평가. 단, 코드도 프롬프트 입력으로 사용됨. Table 6: C2C(코드만) 2.57% vs EoH(thought+code) 0.66% — 약 4배 차이.
- 논문 내 역할: Section 3.1 "Dual representation". 모든 prompt strategy에서 LLM은 먼저 thought를 묘사한 뒤 code 생성.
- 내 추측 검증: **맞다.** 보완: thought는 reasoning뿐 아니라 parent 아이디어 전달의 핵심 매개체.
- 헷갈리는 포인트: T&C2T2C(입력 thought+code, 출력 thought만) 0.85% vs EoH(출력도 thought+code) 0.66%. LLM이 코드를 직접 출력할 때 thought-code 일관성 더 강함.

### Q2 Selection in candidate pool
- 한 줄 요약: Rank 기반 확률적 selection + top-N deterministic selection의 이중 구조.
- selection 기준: Parent 선택 시 p_i ∝ 1/(r_i + N). Population 갱신 시 top-N.
- diversity 고려 여부: 명시적 diversity metric 없음. 5가지 prompt strategy(E1, E2, M1, M2, M3)의 서로 다른 역할로 암묵적 확보.
- 논문 내 역할: Step 1.1에서 parent selection, Step 2에서 population management.
- 내 추측 검증: **부분적으로 맞다.** Top-N은 맞으나, parent selection의 확률적 요소도 포함.
- 헷갈리는 포인트: 두 가지 selection 혼재 — parent(확률적) vs population 갱신(결정적).

### Q3 Mutation loop
- 한 줄 요약: 초기화 → (5 strategy × N개 생성 → 평가 → top-N) × 20 generation.
- 단계별 설명: Step 0(초기화) → Step 1(생성+평가, 5 strategy 병렬 적용) → Step 2(top-N 갱신) → 반복.
- pseudo-code:
```
P = [LLM(init_prompt) for _ in range(N)]  # Step 0
for gen in range(20):                       # 20 generations
    new = []
    for strategy in [E1, E2, M1, M2, M3]:
        for _ in range(N):
            parents = rank_select(P)        # Step 1.1
            h = LLM(strategy_prompt(parents))  # Step 1.2
            h.fitness = evaluate(h)         # Step 1.3
            if feasible(h): new.append(h)   # Step 1.4
    P = top_N(P + new, N)                  # Step 2
```
- stopping condition: 고정 20 generations. 총 ~2,000 LLM calls.
- 내 추측 검증: 5가지 strategy가 매 generation 모두 동시 사용되는 것이 핵심.
- 헷갈리는 포인트: "Feasible" = syntax error 없이 실행 가능한 경우. 5N 중 feasible한 것만 추가.

### Q4 Set of problems
- 한 줄 요약: 여러 instance로 구성된 set에서 평가하여 과적합 방지.
- 정의: Bin packing: Weibull 5k items × C=100의 5개 instance. TSP: 100 nodes × 64 instances.
- 왜 필요한가: 단일 instance에 특화된 heuristic 방지.
- overfitting과의 관계: Table 5에서 EoH-e1이 C=100 훈련에서 C=500 테스트 시 58.17% gap. EoH는 2.13%로 일반화.
- 내 추측 검증: **맞다.**
- 헷갈리는 포인트: Training instance set과 test instance set 구분이 명시적 "train/test split"으로 표현되지 않음.

## 7) 마지막 정리
- 이 논문의 핵심 아이디어: Thought+code 공진화가 FunSearch 대비 500배 적은 LLM query로 동등 이상 성능.
- 실제 구현 포인트: N=20, 20 generations, 5 strategies. p_i ∝ 1/(r_i + N). GitHub: https://github.com/FeiLiu36/EoH
- 후속 질문: E2가 generalization에 중요한 이유? N과 generation 수 trade-off? Feasibility check 실패율?
```
---
[Paper 5] ReasoningBank
```md
# ReasoningBank

## 1) 내가 이해한 배경
- ReasoningBank는 reasoning data / memory / test-time scaling / verifier 계열과 연결된 것으로 보인다.
- 나는 memory, test-time scaling, MaTTS, 그리고 비교 기준이 되는 decoding/verification 기법들이 헷갈린다.

## 2) 내가 원하는 답변 스타일
- 개념 비교 위주
- 서로 비슷한 용어를 표처럼 구분해줘
- 가능하면 inference-time 관점에서 설명해줘

## 3) 핵심 질문
1. Memory는 정확히 무엇을 의미하는가?
2. Test-Time Scaling이란 무엇인가?
3. MaTTS는 무엇인가?
4. 기존에 말하는 Best-of-N / Beam Search / Leveraging Verifier는 각각 무엇인가?
5. 이들이 서로 어떻게 다른가?

## 4) 내 현재 추측
- memory는 단순 context window가 아니라, 이전 reasoning trace나 solved example bank를 저장/검색하는 구조일 수도 있다.
- test-time scaling은 학습이 아니라 추론 시점에 compute를 더 써서 성능을 높이는 방법 같긴 하다.
- MaTTS는 memory-augmented test-time scaling 류일 것 같다.
- Best-of-N / Beam Search / Verifier는 모두 test-time에 후보를 여러 개 만들고 걸러내는 계열로 보인다.

## 5) Claude에게 요구할 것
- 각 용어를 서로 비교해서 설명해줘.
- memory가 저장하는 객체와, inference 시 어떻게 쓰이는지 설명해줘.
- test-time scaling을 compute allocation 관점에서 설명해줘.
- MaTTS가 기존 Best-of-N / Beam / Verifier 방식과 무엇이 다른지 말해줘.
- 내 추측을 항목별로 검증해줘.

## 6) 답변 공간

### Q1 Memory
- 한 줄 요약: 과거 경험(성공+실패)에서 일반화 가능한 고수준 추론 전략을 추출하여 title/description/content 스키마로 저장하는 구조화된 메모리.
- 정의: raw trajectory가 아니라 추상화된 원칙(actionable principles)의 집합. 단순 context window 확장이 아님.
- 무엇을 저장하는가: (1) Title: 전략 한 줄 식별 (2) Description: 한 문장 요약 (3) Content: 구체적 추론 단계·결정 근거. JSON 형식, embedding 사전 계산.
- 어떻게 사용하는가: 3단계. (i) Retrieval: cosine similarity로 top-k(기본 k=1) 검색 → system instruction에 주입, (ii) Extraction: LLM-as-a-Judge가 성공/실패 판정 후 전략 추출, (iii) Consolidation: ReasoningBank에 append.
- 내 추측 검증: **방향 맞지만 수정 필요.** Raw trace가 아니라 증류한 고수준 전략을 저장. k=1이 default.
- 헷갈리는 포인트: 실패 trajectory도 저장. 기존 방법은 실패 추가 시 -2.2% 하락이지만 ReasoningBank는 +3.2% 향상.

### Q2 Test-Time Scaling
- 한 줄 요약: 모델 가중치 변경 없이 추론 시점에 compute를 더 투자하여(더 많은 trajectory 생성·정제) 성능 향상.
- 정의: inference 단계에서 추가 계산 자원 활용. 파라미터 고정, 동일 태스크에 대해 더 많은 탐색/반복 정제.
- 왜 필요한가: train-time scaling(더 큰 모델/데이터)은 비용이 높음. TTS는 재학습 없이 성능 향상.
- compute 관점 설명: (a) Parallel: k개 trajectory 병렬 생성 (b) Sequential: self-refinement로 반복 정제. k=1~5 범위 실험.
- 내 추측 검증: **정확히 맞다.** 단, 핵심 주장은 "TTS 단독은 불충분, 메모리와 결합해야 효과적."
- 헷갈리는 포인트: "경험 스케일링" = task 수(breadth)가 아니라 task당 탐색 깊이(depth) 늘리는 것.

### Q3 MaTTS
- 한 줄 요약: 메모리↔scaling 양방향 시너지. 더 많은 compute → 더 풍부한 경험 → 더 고품질 메모리 → 더 효과적 scaling.
- 정의: ReasoningBank + TTS 결합. 여러 trajectory의 대조 신호(contrastive signal)로 고품질 메모리 추출.
- pipeline 내 역할: (1) Parallel MaTTS: k개 trajectory → self-contrast로 비교 → 최대 5개 메모리 추출. (2) Sequential MaTTS: 반복 정제 → intermediate notes도 메모리 신호.
- 기존 기법 대비 차이: Vanilla TTS는 각 trajectory 독립 변환. MaTTS는 cross-trajectory 대조 신호 활용. WebArena k=5: MaTTS 55.1 vs Vanilla 52.4 vs No memory 41.7.
- 내 추측 검증: **맞다.** 단, "memory-augmented"가 단방향이 아니라 양방향.
- 헷갈리는 포인트: Vanilla TTS와 MaTTS 차이가 미묘. 핵심은 joint 분석 vs 독립 분석.

### Q4 Baselines / related methods
- Best-of-N:
  - 정의: k개 trajectory 중 LLM 평가자가 최선 1개 선택.
  - 장단점: 장점: 단순. 단점: k-1개 경험 폐기, 메모리 없으면 제한적(+3.2에 불과).
- Beam Search:
  - 정의: step 단위로 상위 beam 후보 유지.
  - 장단점: 장점: step 단위 다양성. 단점: compute 높고 multi-turn에 복잡, 메모리 없음.
- Leveraging Verifier:
  - 정의: 외부 verifier가 step/trajectory 평가.
  - 장단점: 장점: 세밀한 피드백. 단점: 신뢰할 verifier 필요, 메모리 없음.
- 서로의 차이: BoN=trajectory 수준 필터, Beam=step 수준 탐색, Verifier=외부 신호 의존. 셋 다 메모리 학습 없음. MaTTS만 미래 태스크까지 개선.
- 내 추측 검증: **정확히 맞다.**

### 비교 정리 테이블
| 기법 | 추가 compute 사용처 | 메모리 활용 | 핵심 원리 |
|------|-------------------|------------|----------|
| Best-of-N | k개 trajectory 병렬 + LLM 채점 | 없음(단발 선택) | k개 중 1개 선택 |
| Beam Search | step별 top-b 후보 유지 | 없음 | step 단위 다양성 + 가지치기 |
| Verifier | trajectory/step + verifier 평가 | 없음(단기 피드백) | 외부 reward model이 탐색 안내 |
| MaTTS | k개 trajectory + joint self-contrast | ReasoningBank에 축적·활용 | 메모리↔scaling 양방향 시너지 |

## 7) 마지막 정리
- 이 논문의 핵심 아이디어: 성공+실패에서 고수준 전략 증류 + MaTTS로 메모리↔scaling 선순환 → 에이전트 자기진화.
- 실제 구현 포인트: title/description/content 3필드, LLM-as-a-Judge(temperature=0.0), gemini-embedding-001+cosine k=1, WebArena: 40.5→48.8→51.8→55.1%, SWE-Bench: 34.2→38.8%.
- 후속 질문: k=1 최적인 이유? Memory consolidation 고도화 시 이득? 실패 비율이 높을 때 품질 변화? cross-domain transfer?
```
---
