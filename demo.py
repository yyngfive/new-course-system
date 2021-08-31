# 一个获取课表的示例
from courses import Courses
my_courses = Courses(username='xxx',password='xxx')
my_courses.login()
my_courses.get_student_info()
my_courses.get_courses()
for course in my_courses.courses:
    name = course['courseName']
    print(name)