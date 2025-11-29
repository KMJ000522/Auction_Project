📄 프로젝트 진행 상황 보고 (11/29 업데이트)
주제: 경매 핵심 로직 구현 (입찰 경쟁, 자동 환불, 낙찰 정산 시스템)

1. 프로젝트 구조 (App Architecture)
기존 3개 앱 구조 유지 및 역할 심화

users: 회원 인증(JWT) 및 프로필 관리

auctions: 경매 생명주기 관리 + 입찰 경쟁 로직(Bidding Competition) 추가

payments: 재화(Wallet) 관리 + 환불/정산(Settlement) 비즈니스 로직 모델단 구현

2. DB 모델링 및 데이터 무결성 (Database Integrity)
WalletManager 확장 :

단순 입출금을 넘어 refund_for_outbid(상위 입찰 시 환불), settle_winning_bid(낙찰 정산) 메서드를 Manager에 구현하여 비즈니스 로직을 캡슐화함.

Django Signals 활용: 유저 생성 시 Profile과 Wallet 자동 생성 (휴먼 에러 방지).

Status 관리: 경매 상태에 NO_BIDS(유찰) 추가하여 예외 상황 처리.

3. 핵심 기술 구현 (Key Features)
입찰 경쟁 및 자동 환불 시스템 (Auto-Refund):

더 높은 입찰이 들어오면, 기존 1등의 잠긴 재화(locked_balance)를 즉시 풀어주는(balance) 로직을 transaction.atomic 내에서 원자적으로 처리.

재화 잠금 및 정산 (Fund Locking & Settlement):

입찰 시: 내 돈이 즉시 locked 상태로 전환되어 중복 사용 방지.

낙찰 시: 낙찰자의 locked 재화가 차감되고, 판매자의 balance로 즉시 이전되는 정산 로직 구현.

동시성 제어 (Concurrency Control):

돈이 오가는 모든 순간(입찰, 환불, 정산)에 select_for_update를 적용하여 데이터 정합성 100% 보장.

4. 진행 현황
재화 사이클 완성: [충전] → [입찰(잠금)] → [경쟁(환불)] → [종료(정산/이체)] 전 과정 테스트 완료.

API 구현: 입찰(POST /bid), 경매 종료(POST /close) API 연동 완료.

Github: 최신 로직 반영하여 Push 완료.

🗣️ Q&A
Q1. 앱을 굳이 3개로 나눈 이유? 
A. DDD(도메인 주도 설계) 관점에서 기능 분리함. 회원(users), 돈(payments), 경매(auctions)는 성격이 완전히 달라서, 나중에 유지보수하거나 확장할 때 코드 섞이지 않게 처음부터 물리적으로 나눠둠.

Q2. 동시성 제어(select_for_update) 왜 씀?
A. 경매 특성상 마감 직전 동시 입찰 확률 높음. 이때 데이터 꼬여서 돈만 나가고 입찰 씹히는 Race Condition(경쟁 상태) 막으려고, DB 트랜잭션 레벨에서 아예 줄 세우는 비관적 락(Pessimistic Lock) 방식 적용함.

Q3. N+1 문제는 어떻게 해결함? 
A. 리스트 조회할 때 판매자(User) 정보 가져오느라 쿼리 폭발하는 거 확인. select_related 사용해서 SQL JOIN처럼 데이터 한 번에 긁어오도록 쿼리 최적화 끝냄.

Q4. Signals는 왜 씀? 
A. 회원가입 로직 짤 때마다 지갑 생성 코드 일일이 넣으면 누락 실수 생김. 그래서 유저 생성 이벤트 터지면 자동으로 지갑도 만들어지게 강제해서 데이터 무결성 챙김.

Q5. Session 대신 JWT 쓴 이유? 
A. 나중에 프론트 분리하거나 앱으로 확장할 거 대비해서, 서버가 상태 저장 안 하는 Stateless 방식이 유리하다 판단함. DRF 국룰인 Simple JWT 채택.

Q6. 상위 입찰자 나오면 기존 1등 돈은 어케 처리함? 
A. 입찰 API 호출 시 트랜잭션 안에서 '현재 1등' 있는지 먼저 체크함. 있으면 refund_for_outbid 메서드로 묶인 돈(Locked) 즉시 풀어주고(Balance), 그 다음 새 입찰 진행하도록 순차적 로직으로 짬.

Q7. 경매 끝나면 정산은 어떻게 됨? 
A. 종료(close) 요청 들어오면, [낙찰자 돈 차감 -> 판매자 입금] 과정을 하나의 트랜잭션으로 묶어버림. 중간에 에러 나면 아예 없던 일로 롤백돼서, 돈 증발하거나 복사되는 사고 원천 차단함.

Q8. 자기가 올린 거에 자기가 입찰해서 가격 올리는 거 막음? 
A. API 단에서 if auction.seller == request.user 조건 걸어서, 판매자는 자기 거에 입찰 못 하게 어뷰징 방지 로직 박아둠.
