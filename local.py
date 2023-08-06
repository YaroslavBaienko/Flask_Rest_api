import requests

# res = requests.get("http://127.0.0.1:3000/api/main")
res_courses = requests.post("http://127.0.0.1:3000/api/courses", json={"name": "Dj", "videos": 662})
# res_courses = requests.get("http://127.0.0.1:3000/api/courses/0")
# res_courses = requests.delete("http://127.0.0.1:3000/api/courses/24", json={"name": "GOLANG", "videos": 3})
print(res_courses.json())
