from faker import Faker
from faker.providers import internet

fake = Faker()
# 生成名字
print(fake.name())
# 生成地址
print(fake.address())
# 生成国家
print(fake.country())
# 生成省份
print(fake.province())
# 生成市　县
print(fake.city_suffix())
# 生成区
print(fake.district())
# 生成街道名
print(fake.street_name())
# 生成街　路
print(fake.street_suffix())
#　生成０～９　随机数
print(fake.random_digit())
# 生成随机字母
print(fake.random_element())
# 生成随机颜色名
print(fake.color_name())
# 生成随机日期
print(fake.date())
# 生成一段文字
print(fake.text())

fake.add_provider(internet)

# 生成ipv4
print(fake.ipv4_private())

