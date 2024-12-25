from vpython import sphere, vector, rate, color, scene
import numpy as np
import matplotlib.pyplot as plt
import time
import math
from tkinter import *

#설정창 설정
root = Tk()
root.title("Settings")
root.geometry("400x450")

def update_values(event):
    slider1_value = slider1.get()
    slider2_value = slider2.get()
    slider3_value = slider3.get()
    slider4_value = slider4.get() 
    label.config(text=f"r1: {slider1_value}e9, r2: {slider2_value}e9, m1: {slider3_value}e32, m2: {slider4_value}e24")
    
def apply():
    global r1,r2,m1,m2
    r1 = int(slider1.get())
    r2 = int(slider2.get())
    m1 = slider3.get()
    m2 = slider4.get()
    root.destroy()
    

#슬라이더,버튼 생성
slider1 = Scale(root, from_=1, to=100, orient="horizontal", label="Star Radius(*1e9m)", length = 350)
slider1.pack(pady=10)
slider2 = Scale(root, from_=1, to=20, orient="horizontal", label="Planet Radius(*1e9m)", length = 350)
slider2.pack(pady=10)
slider3 = Scale(root, from_=1, to=100, orient="horizontal", label="Star Mass(*1e32kg)", length = 350)
slider3.pack(pady=10)
slider4 = Scale(root, from_=1, to=20, orient="horizontal", label="Planet Mass(*1e24kg)", length = 350)
slider4.pack(pady=10)
btn1 = Button(root, text='Apply', command=apply)

slider1.set(15) #ne9
slider2.set(3)
slider3.set(2) #ne32
slider4.set(6) #ne24

label = Label(root, text="r1: 15e9, r2: 3e9, m1: 2e32, m2: 6e24")
label.pack(pady=20)
btn1.pack(pady=10)

slider1.bind("<Motion>", update_values) 
slider2.bind("<Motion>", update_values)
slider3.bind("<Motion>", update_values) 
slider4.bind("<Motion>", update_values)  

root.mainloop()



#시뮬레이터 설정
G = 6.67430e-11  # (m^3 kg^-1 s^-2)

star = sphere(pos=vector(0, 0, 0), radius=pow(10,9)*r1, color=color.yellow, mass=pow(10,32)*m1)
planet = sphere(pos=vector(1.5e11, 0, 0), radius=pow(10,9)*r2, color=color.blue, mass=pow(10,24)*m2)
planet.velocity = vector(0, 297800, 0) 

t_data, x_data, y_data, z_data, S_data = [], [], [], [], []
time_step = 0.1


#그래프 설정
plt.ion() 
fig, (az, ay, ax, aS) = plt.subplots(4,1)
fig.set_size_inches(8, 6)
line_x, = ax.plot([], [], lw=2)
line_y, = ay.plot([], [], lw=2)
line_z, = az.plot([], [], lw=2)
line_S, = aS.plot([], [], lw=2)

# 그래프 범위 설정
ax.set_xlabel('Time (s)')
ay.set_xlabel('Time (s)')
az.set_xlabel('Time (s)')
ax.set_ylabel('Z Position (m)')
ay.set_ylabel('Y Position (m)')
az.set_ylabel('X Position (m)')
aS.set_xlabel('Time (s)')
aS.set_ylabel('Brightness')

#시뮬레이션 시간 설정
dt = 60 * 60  #1시간 단위로 진행
firstTime = time.time()

scene.width = 640 
scene.height = 360 
scene.range = 3e12 
scene.autoscale = True 

scene.camera.pos = vector(0, 0, 0)  #카메라 위치 조정
scene.camera.axis = vector(1e11, -1e11, 0)  #카메라 시점 설정

plt.show()

# 정사영 구하기 
def project_to_2d(obj, camera_pos, camera_axis):
    to_object = obj.pos - camera_pos
    projection_plane = to_object - to_object.proj(camera_axis)
    return vector(projection_plane.x, projection_plane.y, 0), to_object.dot(camera_axis)

# 가시 단면적 계산하기
def area(x1, y1, r1, x2, y2, r2):
    d = math.sqrt((x2 - x1)**2 + (y2 - y1)**2) 
    rr1 = r1**2
    rr2 = r2**2

    if d >= r1 + r2: 
        return math.pi * rr1
    elif d <= abs(r1 - r2): 
        if r1 > r2: 
            return math.pi * rr1 - math.pi * rr2
        else:
            return 0
    else:  
        try:
            phi = 2 * math.acos((rr1 + d**2 - rr2) / (2 * r1 * d))
            theta = 2 * math.acos((rr2 + d**2 - rr1) / (2 * r2 * d))
        except ValueError:
            return math.pi * rr1 

        overlap_area = 0.5 * rr1 * (phi - math.sin(phi)) + 0.5 * rr2 * (theta - math.sin(theta))
        visible_area = math.pi * rr1 - overlap_area
        return max(visible_area, 0) #값이 튀는 경우 0으로 처리함

# 시뮬레이션 시작
while True:
    rate(1000)  # 시뮬레이션 속도 (초당 1000번 반복)

    # 중력 계산 및 위치 갱신
    r = planet.pos - star.pos
    distance = r.mag
    force = -G * star.mass * planet.mass / distance**2 * r.norm()
    acceleration = force / planet.mass
    planet.velocity += acceleration * dt
    planet.pos += planet.velocity * dt

    star_2d, star_cam_dist = project_to_2d(star, scene.camera.pos, scene.camera.axis)
    planet_2d, planet_cam_dist = project_to_2d(planet, scene.camera.pos, scene.camera.axis)
    
    
    #행성이 가려진 경우 예외처리
    if planet_cam_dist > star_cam_dist:
        result = math.pi * star.radius**2 
    else:
        result = area(star_2d.x, star_2d.y, star.radius, planet_2d.x, planet_2d.y, planet.radius)

    elapsed_time = time.time() - firstTime

    # 데이터 저장
    t_data.append(elapsed_time)
    x_data.append(planet.pos.x)
    y_data.append(planet.pos.y)
    z_data.append(planet.pos.z)
    S_data.append(result)

    # 반응형 그래프 범위 업데이트
    ax.set_xlim(min(t_data), max(t_data))
    ay.set_xlim(min(t_data), max(t_data))
    az.set_xlim(min(t_data), max(t_data))
    ax.set_ylim(min(x_data), max(x_data))
    ay.set_ylim(min(y_data), max(y_data))
    az.set_ylim(min(z_data), max(z_data))
    aS.set_xlim(min(t_data), max(t_data))
    aS.set_ylim(4, math.pi * star.radius**2) 

    # 그래프 데이터 업데이트
    line_x.set_data(t_data, x_data)
    line_y.set_data(t_data, y_data)
    line_z.set_data(t_data, z_data)
    line_S.set_data(t_data, S_data)

    # 그래프 그리기
    plt.draw()
    plt.pause(0.01)