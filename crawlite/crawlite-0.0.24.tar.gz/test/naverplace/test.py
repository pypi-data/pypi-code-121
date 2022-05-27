from .crawler import crawl_naver_place


places = [
    "후라토식당 아브뉴프랑 판교점",
    # "후라토식당 발산역점",
    # "후라토식당 잠실직영점",
    "후라토식당 역삼점",
    # "후라토식당 상암점",
    # "후라토식당 성수점",
    # "후라토식당 상수직영점",
    "후라토식당 경복궁 본점",
    # "후라토식당 여의도직영점",
    # "후라토식당 용산점",
    # "후라토식당 아브뉴프랑광교점",
    "후라토식당 동탄레이크꼬모점",
    # "후라토식당 대구앞산점",
    # "후라토식당 역북점",
    # "후라토식당 트리플스트리트점",
    "후라토식당 충주점",
    # "후라토식당 분당정자점",
    # "후라토식당 배곧점",
    "후라토식당 수유점",
    # "홍콩익스프레스 본점",
    "우동스테이션",
]

def test_naverplace_results_collecting():
    print("----- test for results collecting -----")
    for p in places:
        results = crawl_naver_place(p)
        for k, v in results.items():
            print(f"name:{k} count:{len(v)}")
    print("----- end test for results collecting -----")
