"""Idempotent cross-batch consistency reconciliation edits (90 entries across 29 batches)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# id -> (batch_stem, list_of_(old_substr, new_substr), note_suffix)
EDITS: dict[str, tuple[str, list[tuple[str, str]], str]] = {
    # 01. lay to rest -> 안식을 주다 / 안식에 들게 하다
    "MAIN-4089b3b3316cc2b2": ("004_main", [("떠도는 유령을 안식시키는 사제.", "떠도는 유령에게 안식을 주는 사제.")], "표현 통일(‘안식시키다’ → ‘안식을 주다’)"),
    "MAIN-42ec6c8956180660": ("004_main", [("유령을 안식시켜 줄 거예요.", "유령에게 안식을 줄 거예요.")], "표현 통일(‘안식시키다’ → ‘안식을 주다’)"),
    "MAIN-5e77984033f2d70e": ("004_main", [("유령 셋을 안식시켜요.", "유령 셋에게 안식을 줘요.")], "표현 통일(‘안식시키다’ → ‘안식을 주다’)"),
    "MAIN-3ce32e3b3d3e1c49": ("005_main", [("사제가 안식시킬 때까지", "사제가 안식에 들게 할 때까지")], "표현 통일(‘안식시키다’ → ‘안식에 들게 하다’)"),
    "MAIN-da68ab8b5c7ba067": ("005_main", [("떠도는 유령을 안식시켜요.", "떠도는 유령에게 안식을 줘요.")], "표현 통일(‘안식시키다’ → ‘안식을 주다’)"),
    "MAIN-e87c482045025dfe": ("021_main", [("유령 셋을 안식시켜요.", "유령 셋에게 안식을 줘요.")], "표현 통일(‘안식시키다’ → ‘안식을 주다’)"),
    "MAIN-61cb27c73165868a": ("027_main", [("유령을 안식시켜 줄 거예요.", "유령에게 안식을 줄 거예요.")], "표현 통일(‘안식시키다’ → ‘안식을 주다’)"),
    "MAIN-b7fe705649264dba": ("030_main", [("떠도는 유령을 두 배 빨리 안식시켜요.", "떠도는 유령에게 두 배 빨리 안식을 줘요.")], "표현 통일(‘안식시키다’ → ‘안식을 주다’)"),
    "MAIN-0d8c442cf2cbdc46": ("036_main", [("유령을 편히 쉬게 해 줄 거예요.", "유령에게 안식을 줄 거예요.")], "유사 문구 표현 통일(‘안식을 주다’)"),

    # 02. binge -> 폭식 & colon fix
    "MAIN-cf145582ecd7dfe1": ("023_main", [("흥청망청 노는 중", "폭식 중")], "용어 통일(on a binge → ‘폭식 중’)"),
    "MAIN-5591eb565ceee8ea": ("028_main", [("더는 못 견디고 흥청망청 먹고 써 버려요.", "더는 못 견디고 폭식해요.")], "용어 통일(goes on a binge → ‘폭식해요’)"),
    "MAIN-8973e7b85ba3b6fe": ("032_main", [("더는 못 견디고 흥청망청 놀아나요: 국고에서 {1}, 그리고 지갑을 통째로.", "더는 못 견디고 폭식해요 – 국고에서 {1}, 그리고 지갑까지 통째로.")], "용어 통일(‘폭식해요’) 및 동사 어미 뒤 콜론 정리"),

    # 03. UI header / + cohort / .po header
    "MAIN-b76fbee515c47867": ("014_main", [("코드 창 상단의 +를 누르면 쉬고 있는 영웅 한 명이 더 같은 파일을 실행해요.", "코드 창 제목 표시줄의 +를 누르면 쉬고 있는 영웅 한 명이 같은 파일을 추가로 실행해요.")], "용어 통일(‘제목 표시줄’) 및 어순 다듬기"),
    "MAIN-5a38b63a0cefe50c": ("018_main", [("제목 줄에 초록색 ▶ 버튼이 있어요.", "제목 표시줄에 초록색 ▶ 버튼이 있어요.")], "용어 통일(‘제목 표시줄’)"),
    "MAIN-ad190e87ce1de7a2": ("018_main", [("제목 줄의 ▶를 누르세요(F5).", "제목 표시줄의 ▶를 누르세요(F5).")], "용어 통일(‘제목 표시줄’)"),
    "MAIN-dc1b3271497e6fca": ("019_main", [("제목 줄의 <b>▶</b>를 누르세요(또는 F5).", "제목 표시줄의 <b>▶</b>를 누르세요(또는 F5).")], "용어 통일(‘제목 표시줄’)"),
    "MAIN-5854557aae8d082c": ("028_main", [("제목 줄의 ▶를 누르세요(F5).", "제목 표시줄의 ▶를 누르세요(F5).")], "용어 통일(‘제목 표시줄’)"),
    "MAIN-5c1ebb1870cf0706": ("028_main", [("코드 창 제목 줄의 +를 누르면 쉬고 있는 영웅 한 명이 더 같은 파일을 실행해요.", "코드 창 제목 표시줄의 +를 누르면 쉬고 있는 영웅 한 명이 같은 파일을 추가로 실행해요.")], "용어 통일(‘제목 표시줄’) 및 어순 다듬기"),
    "MAIN-e18b375fa76f2803": ("028_main", [("제목 줄의 <b>▶</b>를 누르세요(또는 F5).", "제목 표시줄의 <b>▶</b>를 누르세요(또는 F5).")], "용어 통일(‘제목 표시줄’)"),
    "MAIN-561e4edb7100ee68": ("031_main", [("머리글이 있는 lang/<code>.po", "헤더가 있는 lang/<code>.po")], ".po 파일 용어 통일(‘헤더’)"),
    "MAIN-80d472efdeb2bbd7": ("032_main", [("머리글에는 언어(Language-Name)", "헤더에는 언어(Language-Name)")], ".po 파일 용어 통일(‘헤더’)"),

    # 04. slot naming
    "MAIN-ab93b23f769653a1": ("028_main", [("규칙 이름을 딴 함수", "슬롯 이름을 딴 함수")], "오역·불일치 통일(‘규칙 이름’ → ‘슬롯 이름’)"),

    # 05. guardhouse -> 초소, Fire Warden -> 화재 감시원, Town guard -> 마을 경비대
    "MAIN-9480ca13da12b3e1": ("006_main", [("경비 초소 문에 붙여 둘", "초소 문에 붙여 둘")], "건물명 통일(Guardpost/guardhouse → ‘초소’)"),
    "MAIN-7df4a153b839e749": ("018_main", [("경비 초소 문에 붙일 그림:", "초소 문에 붙일 그림:")], "건물명 통일(Guardpost/guardhouse → ‘초소’)"),
    "MAIN-672cba8a3d432b1c": ("017_main", [("화재 감독관", "화재 감시원")], "역할명 통일(Fire Warden → ‘화재 감시원’)"),
    "MAIN-09ab80215a97caac": ("030_main", [("화재 감시꾼:", "화재 감시원:")], "역할명 통일(Fire Warden → ‘화재 감시원’)"),
    "MAIN-ab0b02a0f605665e": ("036_main", [("도시 경비대", "마을 경비대")], "용어 통일(Town Guard → ‘마을 경비대’)"),

    # 06. heating Wood -> 목재 & log unit alignment
    "MAIN-cae40fdd71b5433a": ("032_main", [("집은 장작을 두 배로 때지만,", "집은 목재를 두 배로 때지만,")], "자원명 통일(wood → ‘목재’)"),
    "MAIN-6edc8a59e6ce38ed": ("032_main", [("집은 장작을 두 배로 때고,", "집은 목재를 두 배로 때고,")], "자원명 통일(wood → ‘목재’)"),
    "MAIN-06d78bdb5aeef0cd": ("032_main", [("집은 장작을 두 배로 때요.", "집은 목재를 두 배로 때요.")], "자원명 통일(wood → ‘목재’)"),
    "MAIN-22e885cd77246867": ("032_main", [("집은 장작을 두 배로 때요.", "집은 목재를 두 배로 때요.")], "자원명 통일(wood → ‘목재’)"),
    "MAIN-b57e6a8df0be9a9f": ("032_main", [("국고에 불 땔 장작이 없어", "국고에 불 땔 목재가 없어")], "자원명 통일(wood → ‘목재’)"),
    "MAIN-70798e68a2802413": ("032_main", [("난방에 분당 장작 {0}개를 때요.", "난방에 분당 목재를 {0}씩 때요.")], "자원명·단위사 통일(‘목재’, ‘개’ 제거)"),
    "MAIN-2a88602cc691df66": ("033_main", [("난방에 분당 장작 {0}개를 때요.", "난방에 분당 목재를 {0}씩 때요.")], "자원명·단위사 통일(‘목재’, ‘개’ 제거)"),
    "MAIN-e2a314b29fb9dad7": ("033_main", [("이제 집이 장작을 때요.", "이제 집이 목재를 때요."), ("장작이 없으면 춥고 불행해요.", "목재가 없으면 춥고 불행해요.")], "자원명 통일(wood → ‘목재’)"),
    "MAIN-daaf146ffc2517cf": ("033_main", [("들어오는 장작을 다 써요.", "들어오는 목재를 다 써요.")], "자원명 통일(wood → ‘목재’)"),
    "MAIN-a2cda2a05333a558": ("035_main", [("베는 것보다 장작을 더 때요", "베는 것보다 목재를 더 때요")], "자원명 통일(wood → ‘목재’)"),
    "MAIN-3779c898d4a8b7d4": ("039_main", [("난방에 분당 목재 {0}개씩 때요.", "난방에 분당 목재를 {0}씩 때요.")], "자원 단위사 제거(‘목재 {0}개’ → ‘목재를 {0}씩’)"),
    "MAIN-835ce6a3d2bbeb2f": ("041_main", [("집마다 통나무 반 개, 오두막마다 한 개,", "집마다 반 개, 오두막마다 한 개,")], "난방 목재 단위 표현 통일(‘반 개, 한 개’)"),

    # 07. appearance (skin tone + fair hair)
    "MAIN-99efcea2348caecb": ("022_main", [("밝음", "밝은 톤")], "피부 톤 표기 자연스럽게 통일"),
    "MAIN-582fb20d0b965a73": ("022_main", [("어두움", "어두운 톤")], "피부 톤 표기 자연스럽게 통일"),
    "MAIN-fcedc493b97d362b": ("023_main", [("중간", "중간 톤")], "피부 톤(medium) 자연스럽게 다듬음"),
    "MAIN-6c4c2d644a91d14c": ("035_main", [("밝은색 머리", "금발")], "용어 통일(fair hair → ‘금발’)"),

    # 08. menu breadcrumbs
    "MAIN-9c15647a7ce221dc": ("013_main", [("메뉴 -> 테마", "메뉴 → 테마")], "메뉴 화살표 기호 통일(-> → →)"),
    "MAIN-c3a71dd67d548d8e": ("034_main", [("‘메뉴 → 모드’에 문제가 나와요.", "메뉴 → 모드에 문제가 나와요.")], "메뉴 경로 따옴표 표기 통일"),
    "MAIN-f4a41c0348c32f57": ("035_main", [("‘메뉴 → 모드’ → ‘모드 폴더 열기’", "메뉴 → 모드 → ‘모드 폴더 열기’")], "메뉴 경로 따옴표 표기 통일"),
    "MAIN-58bdbf3bacf0ce2d": ("035_main", [("‘메뉴 → 테마’에서 바꾸고 ‘저장’을 누르세요.", "메뉴 → 테마에서 바꾸고 ‘저장’을 누르세요.")], "메뉴 경로 따옴표 표기 통일"),
    "MAIN-f0de10fffd376d82": ("038_main", [("‘메뉴 → 테마’에서 바꾸고 ‘저장’을 누르세요.", "메뉴 → 테마에서 바꾸고 ‘저장’을 누르세요.")], "메뉴 경로 따옴표 표기 통일"),

    # 09. children in inheritance & couple decrees
    "MAIN-45530086e19bae87": ("014_main", [("부부가 가질 수 있는 아이 수.", "부부가 가질 수 있는 자녀 수.")], "칙령 항목 용어 통일(‘자녀 수’)"),
    "MAIN-dfe70ef553a8d5ab": ("025_main", [("아이들도 물려받을 거예요.", "자녀도 물려받을 거예요.")], "상속 문맥 용어 통일(‘자녀’)"),
    "MAIN-04132c66741a3e9a": ("027_main", [("아이들도 물려받을 거예요.", "자녀도 물려받을 거예요.")], "상속 문맥 용어 통일(‘자녀’)"),
    "MAIN-af0a0ca4a0c2ab18": ("027_main", [("아이들이 물려받아요.", "자녀가 물려받아요.")], "상속 문맥 용어 통일(‘자녀’)"),
    "MAIN-b4eecf62d526df76": ("028_main", [("아이들이 물려받아요.", "자녀가 물려받아요.")], "상속 문맥 용어 통일(‘자녀’)"),
    "MAIN-17dc9afc65c7dd82": ("038_main", [("부부가 가질 수 있는 아이 수,", "부부가 가질 수 있는 자녀 수,")], "칙령 항목 용어 통일(‘자녀 수’)"),

    # 10. for years
    "MAIN-0394999aeac217d8": ("030_main", [("오랫동안 마을을 돌봤다.", "여러 해 동안 마을을 돌봤다.")], "유사 문구 통일(‘여러 해 동안’)"),
    "MAIN-f29e23e2e1c00844": ("030_main", [("오랫동안 마을을 돌보다가", "여러 해 동안 마을을 돌보다가")], "유사 문구 통일(‘여러 해 동안’)"),

    # 11. URL placeholder <island>
    "MAIN-d64fd2ed1f63d1bc": ("005_main", [("https://<섬>.isle/prices", "https://<island>.isle/prices")], "URL 자리표시자 표기 통일(<island>)"),
    "MAIN-af9ba326b38a4a2a": ("013_main", [("https://<섬>.isle/…", "https://<island>.isle/…")], "URL 자리표시자 표기 통일(<island>)"),
    "MAIN-7371a46993b67129": ("018_main", [("https://<섬>.isle", "https://<island>.isle")], "URL 자리표시자 표기 통일(<island>)"),

    # 12. creature -> 생물
    "MAIN-86c213cadd959df6": ("004_main", [("동물의 두뇌예요.", "생물의 두뇌예요.")], "용어 통일(creature → ‘생물’)"),
    "MAIN-9bce1b8435a6027f": ("005_main", [("동물의 두뇌까지,", "생물의 두뇌까지,")], "용어 통일(creature → ‘생물’)"),
    "MAIN-e8e8a0e039bf762b": ("012_main", [("동물이 알아차리는 것", "생물이 알아차리는 것")], "용어 통일(creature → ‘생물’)"),
    "MAIN-bbc15cb12590e6ff": ("023_main", [("섬의 동물들까지.", "섬의 생물들까지.")], "용어 통일(creature → ‘생물’)"),
    "MAIN-a57cfbc6d954f8e6": ("031_main", [("동물들의 두뇌:", "생물들의 두뇌:")], "용어 통일(creature → ‘생물’)"),

    # 13. Resource counter '개' removal on bulk resources + 041 profession labels
    "STORY-300b16a4d6e12044": ("001_story", [("곡물 %fact:bakery.in.grain%개와 목재 %fact:bakery.in.wood%개를 가져가", "곡물을 %fact:bakery.in.grain%, 목재를 %fact:bakery.in.wood% 가져가")], "비계수 자원(‘곡물·목재’) 단위사 ‘개’ 제거"),
    "STORY-f25337218418a6f6": ("001_story", [("곡물 %fact:crop.grain.yield%개를 국고에 넣어요.", "곡물을 %fact:crop.grain.yield% 국고에 넣어요."), ("곡물 %fact:chapter.grain%개를 수확하세요.", "곡물을 %fact:chapter.grain% 수확하세요.")], "비계수 자원(‘곡물’) 단위사 ‘개’ 제거"),
    "STORY-0dd9f0bc798fc138": ("001_story", [("동화 %fact:research.masonry.copper%닢과 목재 %fact:research.masonry.wood%개로 ‘석공술’을 연구한 다음 채석장을 지으세요.", "‘석공술’을 연구한 다음 채석장을 지으세요(비용: 동화 %fact:research.masonry.copper%닢, 목재 %fact:research.masonry.wood%).")], "비계수 자원(‘목재’) 단위사 ‘개’ 제거"),
    "STORY-05e11d5777f945b9": ("001_story", [("철 %fact:mine.out.iron%개마다 빵 %fact:mine.in.bread%개를 써요.", "철 %fact:mine.out.iron%마다 빵 %fact:mine.in.bread%개를 써요.")], "비계수 자원(‘철’) 단위사 ‘개’ 제거"),
    "STORY-eb627d09d766edf2": ("001_story", [("동화 %fact:research.expansion.copper%닢, 목재 %fact:research.expansion.wood%개, 석재 %fact:research.expansion.stone%개로 ‘새 땅’을 연구하세요.", "‘새 땅’을 연구하세요. 비용: 동화 %fact:research.expansion.copper%닢, 목재 %fact:research.expansion.wood%, 석재 %fact:research.expansion.stone%.")], "비계수 자원(‘목재·석재’) 단위사 ‘개’ 제거"),
    "STORY-d9ce361fab5d7d9b": ("001_story", [("철 %fact:smithy.in.iron%개와 목재 %fact:smithy.in.wood%개로 도구를 %fact:smithy.out.tools%개 만들어요.", "철을 %fact:smithy.in.iron%, 목재를 %fact:smithy.in.wood% 써서 도구를 %fact:smithy.out.tools%개 만들어요.")], "비계수 자원(‘철·목재’) 단위사 ‘개’ 제거"),
    "STORY-499f342e96e90bc0": ("001_story", [("동화 %fact:hire.4.copper%닢, 상품 %fact:hire.4.goods%개, 석재 %fact:hire.4.stone%개로 ‘영웅 길드’를 한 번 더 연구하세요.", "‘영웅 길드’를 한 번 더 연구하세요(비용: 동화 %fact:hire.4.copper%닢, 상품 %fact:hire.4.goods%개, 석재 %fact:hire.4.stone%).")], "비계수 자원(‘석재’) 단위사 ‘개’ 제거"),
    "STORY-ebf8d9d809be7107": ("001_story", [("동화 %fact:hire.3.copper%닢, 목재 %fact:hire.3.wood%개, 석재 %fact:hire.3.stone%개가 들어요.", "비용: 동화 %fact:hire.3.copper%닢, 목재 %fact:hire.3.wood%, 석재 %fact:hire.3.stone%.")], "비계수 자원(‘목재·석재’) 단위사 ‘개’ 제거"),
    "STORY-ec969983bca359fd": ("001_story", [("두 번째 영웅에는 동화 %fact:hire.2.copper%닢과 목재 %fact:hire.2.wood%개가 들어요.", "두 번째 영웅 고용 비용: 동화 %fact:hire.2.copper%닢, 목재 %fact:hire.2.wood%.")], "비계수 자원(‘목재’) 단위사 ‘개’ 제거"),
    "STORY-ff9ea62e746311a4": ("002_story", [("곡물 %fact:chapter.grain%개 수확", "곡물 %fact:chapter.grain% 수확")], "비계수 자원(‘곡물’) 단위사 ‘개’ 제거"),
    "STORY-880d8c0e348aefb2": ("002_story", [("곡물 %fact:chapter.grain%개 수확", "곡물 %fact:chapter.grain% 수확")], "비계수 자원(‘곡물’) 단위사 ‘개’ 제거"),
    "STORY-b8b77887658dab37": ("002_story", [("국고에 목재 %fact:chapter.wood%개와 석재 %fact:chapter.stone%개를 갖춰 두고", "국고에 목재를 %fact:chapter.wood%, 석재를 %fact:chapter.stone% 갖춰 두고")], "비계수 자원(‘목재·석재’) 단위사 ‘개’ 제거"),
    "STORY-1e5005d09edb31a8": ("002_story", [("곡물 %fact:chapter.grain%개를 수확하세요.", "곡물을 %fact:chapter.grain% 수확하세요.")], "비계수 자원(‘곡물’) 단위사 ‘개’ 제거"),
    "STORY-dd1cac74b36f70c4": ("002_story", [("동화 %fact:research.charter.copper%닢, 지식 %fact:research.charter.knowledge%, 상품 %fact:research.charter.goods%개, 목재 %fact:research.charter.wood%개가 들어요.", "비용: 동화 %fact:research.charter.copper%닢, 지식 %fact:research.charter.knowledge%, 상품 %fact:research.charter.goods%개, 목재 %fact:research.charter.wood%.")], "비계수 자원(‘목재’) 단위사 ‘개’ 제거"),
    "STORY-05b658e66a7c90ec": ("002_story", [("기념비는 %fact:size.monument% 크기이고 지식 %fact:monument.cost.knowledge%, 동화 %fact:monument.cost.copper%닢, 석재 %fact:monument.cost.stone%개, 목재 %fact:monument.cost.wood%개, 철 %fact:monument.cost.iron%개가 들어요.", "기념비는 %fact:size.monument% 크기예요(비용: 지식 %fact:monument.cost.knowledge%, 동화 %fact:monument.cost.copper%닢, 석재 %fact:monument.cost.stone%, 목재 %fact:monument.cost.wood%, 철 %fact:monument.cost.iron%).")], "비계수 자원(‘석재·목재·철’) 단위사 ‘개’ 제거"),
    "STORY-57f9f822db0fe989": ("003_story", [("국고에 목재 {1}개와 석재 {2}개를 모아 두세요.", "국고에 목재를 {1}, 석재를 {2} 모아 두세요.")], "비계수 자원(‘목재·석재’) 단위사 ‘개’ 제거"),
    "STORY-1d378944ab960f00": ("003_story", [("곡물 %fact:chapter.grain%개 수확", "곡물 %fact:chapter.grain% 수확")], "비계수 자원(‘곡물’) 단위사 ‘개’ 제거"),
    "STORY-73ee389f4c3ab82f": ("003_story", [("국고에 목재 {0}개와 석재 {1}개가 모자랐어요.", "국고에 목재 {0}, 석재 {1}만큼 모자랐어요.")], "비계수 자원(‘목재·석재’) 단위사 ‘개’ 제거"),
    "MAIN-f0fbefffc9064264": ("038_main", [("다른 건물은 목재 %fact:repair.wood%개와 석재 %fact:repair.stone%개가 들어요.", "다른 건물은 목재 %fact:repair.wood%, 석재 %fact:repair.stone%만큼 들어요.")], "비계수 자원(‘목재·석재’) 단위사 ‘개’ 제거"),
    "MAIN-bfbdb6a6b91fef60": ("041_main", [("TaxCollector는 징수하고, Builder는 짓고 수리하고, Guard는 지켜요.", "징수원(TaxCollector)은 징수하고, 건축가(Builder)는 짓고 수리하고, 경비병(Guard)은 지켜요.")], "영웅 직업명 병기 통일"),

    # 14. particle safety on dynamic tokens
    "MAIN-4d62ace595e58c5d": ("022_main", [("items[{0}]는 {1}.", "items[{0}]의 값은 {1}.")], "동적 인덱스 뒤 조사 충돌 회피"),
    "MAIN-d54e502d9704fe6c": ("022_main", [("items[{0}]는 {1},", "items[{0}]의 값은 {1},")], "동적 인덱스 뒤 조사 충돌 회피"),
    "MAIN-f8b99f662612f82d": ("022_main", [("items[{0}]는 {1}:", "items[{0}]의 값은 {1}:")], "동적 인덱스 뒤 조사 충돌 회피"),
    "MAIN-e525ca30c803abee-P0": ("029_main", [("items[{1}]는 {2}:", "items[{1}]의 값은 {2}:")], "동적 인덱스 뒤 조사 충돌 회피"),
    "MAIN-2bfd3be1c86ad3d2": ("032_main", [("%key:RunLine%은 커서가", "%key:RunLine% 키는 커서가")], "단축키 토큰 뒤 ‘키’ 보완으로 조사 일치"),
    "MAIN-99213bef1d332850": ("034_main", [("%key:GoToDefinition%을 누르면", "%key:GoToDefinition% 키를 누르면")], "단축키 토큰 뒤 ‘키’ 보완으로 조사 일치"),
}


def run(results_dir: Path, apply: bool) -> int:
    by_batch: dict[str, dict[str, tuple[list[tuple[str, str]], str]]] = {}
    for eid, (stem, repls, note_add) in EDITS.items():
        by_batch.setdefault(stem, {})[eid] = (repls, note_add)

    already_applied = 0
    pending = 0
    conflicts = 0
    modified_batches: list[str] = []

    for stem, items in sorted(by_batch.items()):
        path = results_dir / f"{stem}.reviewed.jsonl"
        lines = path.read_text(encoding="utf-8").splitlines()
        new_lines: list[str] = []
        seen: set[str] = set()
        batch_changed = False

        for line in lines:
            if not line.strip():
                continue
            obj = json.loads(line)
            eid = obj["id"]
            if eid in items:
                seen.add(eid)
                repls, note_add = items[eid]
                kr = obj["ko_revised"]
                if all(new in kr for _, new in repls):
                    already_applied += 1
                elif all(kr.count(old) == 1 for old, _ in repls):
                    pending += 1
                    if apply:
                        for old, new in repls:
                            kr = kr.replace(old, new)
                        obj["ko_revised"] = kr
                        old_note = (obj.get("note") or "").strip()
                        if note_add not in old_note:
                            obj["note"] = f"{old_note}; {note_add}" if old_note else note_add
                        batch_changed = True
                else:
                    conflicts += 1
                    print(f"[CONFLICT] {stem} {eid}: {kr!r}")
            new_lines.append(json.dumps(obj, ensure_ascii=False))

        missing = set(items) - seen
        if missing:
            conflicts += len(missing)
            print(f"[MISSING] {stem}: {sorted(missing)}")

        if apply and batch_changed:
            path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            modified_batches.append(stem)

    mode = "APPLY" if apply else "CHECK"
    print(
        f"[{mode}] total_edits={len(EDITS)}, already_applied={already_applied}, "
        f"pending={pending}, conflicts={conflicts}, modified_batches={len(modified_batches)}"
    )
    return 1 if conflicts else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--apply", action="store_true", help="Write pending edits to JSONL files")
    args = parser.parse_args()
    return run(args.results_dir, args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
