import os
import json
import argparse


# 데이터 파일 경로
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


## 데이터 관련 함수
# 데이터 로드
def load_data() -> list:
	try:
		with open(DATA_PATH, "r", encoding="utf-8") as f:
			return json.load(f)
	except FileNotFoundError:
		print("데이터 파일을 찾지 못했습니다.")
		return []


# 데이터 저장
def save_data(restaurant: list):
	with open(DATA_PATH, "w", encoding="utf-8") as f:
		json.dump(restaurant, f, ensure_ascii=False, indent=2)


## 출력 관련 함수
# 음식점 정보 출력
def print_restaurants(information: dict):
	for key, val in information.items():
		print(f"{key}: {val}", end=" ")
	print()


## 전처리 관련 함수
# 기존 데이터들 중 category가 여러개인 데이터를 나누는 함수
def split_category(restaurant: list):
	for information in restaurant:
		if isinstance(information["category"], str):
			information["category"] = information["category"].split('/')
	
	save_data(restaurant)


## 기능 관련 함수
# 모든 음식점의 정보를 출력
def cmd_list(restaurant: list):
	results = []
	
	print("모든 음식점 리스트입니다!")
	for information in restaurant:
		result = ""	
		for key, val in information.items():
			result += f"{key}: {val} "
		results.append(result)
	
	print("\n".join(results))


# 입력받은 keyword의 카테고리에 맞는 음식점 이름 출력
def cmd_category(restaurant: list, keyword: str):
	results = []
	
	print(f"{keyword} 카테고리에 해당하는 음식점 리스트입니다!")
	for information in restaurant:
		name = information["name"]
		category = information["category"]

		for category_name in category:
			if keyword == category_name:
				results.append(name)
				break

	print("\n".join(results))	


# 음식점들의 category 종류 출력
def cmd_show_category(restaurant: list):
	results = set()
	
	print(f"현재 등록된 음식점들의 모든 카테고리 종류입니다!")
	for information in restaurant:
		results |= set(information["category"])
	
	print("category 종류:", *list(results))


# 입력받은 keyword가 음식점 이름에 들어가는 음식점 리스트 출력
def cmd_name(restaurant: list, keyword: str):
	print(f"음식점 이름에 '{keyword}'(이)가 들어가는 음식점 리스트입니다!")
	for information in restaurant:	
		if keyword in information["name"]:
			print_restaurants(information)


# keyword보다 likes 수가 많은 음식점 출력
def cmd_like(restaurant: list, keyword: int):
	
	print(f"좋아요가 {keyword}개 이상인 음식점 리스트입니다!")
	for information in restaurant:
		if keyword <= information['likes']:
			print_restaurants(information)


# like 기준으로 내림차순 정렬 후 상위 keyword 개 음식점 출력
def cmd_popular(restaurant:list, keyword: int):
	
	results = sorted(restaurant, key= lambda x: -x.get("likes", 0))[:keyword]
	
	print(f"좋아요 순 상위 {keyword}개의 음식점 리스트입니다!")
	for result in results:
		print_restaurants(result)


# 해당 음식점 like += 1
def cmd_recommend(restaurant: list, keyword: str):
	found = False
	total_likes = 0

	for information in restaurant:
		if information["name"] == keyword:
			information["likes"] += 1
			total_likes = information["likes"]
			found = True
			break
	if found:
		print(f"{keyword}의 좋아요가 1 올랐습니다! 총 좋아요 수는 {total_likes}개 입니다!")
		save_data(restaurant)
	else:
		print(f"{keyword}에 해당하는 음식점을 찾지 못했습니다.")


# 새로운 음식점 추가
def cmd_new(restaurant: list):
	name = input("가게 이름을 입력해주세요: ").strip()
	print("가격대 입력 예시 - 10000원 이하, 10000원~15000원, 15000원 이상")
	price = input("가격대를 입력해주세요: ").strip()
	category = input("카테고리를 입력해주세요: ").strip().split()

	new_rest = {
		"name": name,
		"price": list(price),
		"likes": 0,
		"category": category
	}
	
	print("새로운 음식점을 추가했습니다!")
	restaurant.append(new_rest)
	save_data(restaurant)


# 모든 명령어의 도움말 출력 -> 미완
def cmd_help():
	explains = [
	("list", "모든 음식점의 정보를 출력", "list"),
	("category <카테고리>", "<카테고리>에 해당하는 음식점 정보 출력", "category 한식"),
	("show_category", "음식점들의 카테고리 종류 출력", "show_category"),
	("name <이름>", "<이름>이 들어간 음식점 정보 출력", "name 양꼬치"),
	("like <숫자>", "좋아요 수가 <숫자> 이상인 음식점 정보 출력", "like 3"),
	("popular <숫자>", "좋아요 수가 많은 순서대로 <숫자> 개수만큼 음식점 정보 출력", "popular 5"),
	("recommend <이름>", "<이름>에 해당하는 음식점의 좋아요 수 +1", "recommend 맥도날드"),
	("new", "새로운 음식점 추가", "new"),
	("help", "명령어들의 도움말 출력", "help"),
	("quit", "프로그램 종료", "quit")
	]
	
	for cmd, description, example in explains:
		print(f"{cmd:<20} | {description:<40} | 예시: {example:<20}")
	

## 메인 함수
def main():
	restaurant = load_data()
	
	print("맛집 검색 CLI에 오신걸 환영합니다!")
	cmd_help()
	
	# 처음 한 번만 실행
	# split_category(restaurant)

	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers(dest="command")
	
	# list -> 전체 음식점
	subparsers.add_parser("list")
		
	# category -> 특정 카테고리 음식점 / 키워드- 카테고리
	category_parser = subparsers.add_parser("category")
	category_parser.add_argument("keyword")
	
	# show_category -> 음식점들의 카테고리 종류 출력
	subparsers.add_parser("show_category")
	
	# name -> 이름 들어간 음식점 / 키워드- 이름
	name_parser = subparsers.add_parser("name")
	name_parser.add_argument("keyword")
	
	# like -> 일정 좋아요 개수 이상 음식점 / 키워드- 좋아요 개수
	like_parser = subparsers.add_parser("like")
	like_parser.add_argument("keyword", type=int)
	
	# popular -> 인기 음식점 / 키워드- 상위 인기 음식점 개수
	popular_parser = subparsers.add_parser("popular")
	popular_parser.add_argument("keyword", type=int)

	# recommend -> 추천하기 / 키워드 - 추천할 음식점 이름
	recommend_parser = subparsers.add_parser("recommend")
	recommend_parser.add_argument("keyword")

	# new -> 새로운 음식점 추가 / 키워드 - 새로운 음식점 이름
	subparsers.add_parser("new")

	# help -> 각 기능 도움말
	subparsers.add_parser("help")


	while True:
		user_input = input("입력중@@ ").strip()
		if not user_input:
			continue
		if user_input.lower() == "quit":
			print("종료")
			break

		try:
			args = parser.parse_args(user_input.split())
		except SystemExit:
			print("오류가 발생했습니다!")
			continue

		command = args.command.lower()
	
		# 분기
		if command == "category":
			cmd_category(restaurant, args.keyword)
		elif command == "show_category":
			cmd_show_category(restaurant)
		elif command == "list":
			cmd_list(restaurant)
		elif command == "name":
			cmd_name(restaurant, args.keyword)
		elif command == "like":
			cmd_like(restaurant, args.keyword)
		elif command == "popular":
			cmd_popular(restaurant, args.keyword)
		elif command == "recommend":
			cmd_recommend(restaurant, args.keyword)
		elif command == "new":
			cmd_new(restaurant)
		elif command == "help":
			cmd_help()


	return

if __name__ == "__main__":
	main()
