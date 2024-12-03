# 필요한 라이브러리 import
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
import ctypes
import os
import zipfile
import time
from werkzeug.utils import secure_filename
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'dkssud!dlrjs!vmfaldxlavmfzhemdla~' # 세션 암호화 위한 키

UPLOAD_FOLDER = 'static/uploads' # 회원가입에서 업로드한 파일 관리
USER_INFO_FOLDER = 'static/users' # admin에게 전달할 사용자 정보 폴더
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
app.config['USER_INFO_FOLDER'] = USER_INFO_FOLDER

# 폴더들이 없다면 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(USER_INFO_FOLDER):
    os.makedirs(USER_INFO_FOLDER)

# C에서 구현한 함수를 사용하기 위해 dll파일 불러옴
c_function = ctypes.CDLL(os.path.join(os.path.dirname(__file__), r'c_function\C_function.dll'))

# 로그인 함수
c_function.login.restype = ctypes.c_int
c_function.login.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

# 회원가입 요청 함수
c_function.signup_request.restype = ctypes.c_bool
c_function.signup_request.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]

# 아이디 중복확인 함수
c_function.duplicate_check.restype = ctypes.c_bool
c_function.duplicate_check.argtypes = [ctypes.c_char_p]

# 회원가입 수락 함수
c_function.signup_accept.restype = ctypes.c_bool
c_function.signup_accept.argtypes = [ctypes.c_char_p]

# 회원가입 거절 함수
c_function.signup_reject.restype = ctypes.c_bool
c_function.signup_reject.argtypes = [ctypes.c_char_p]

# delete_user 함수 설정
c_function.delete_user.restype = ctypes.c_bool
c_function.delete_user.argtypes = [ctypes.c_char_p]

# is_user_mentor 함수 정의
c_function.is_user_mentor.argtypes = [ctypes.c_char_p]
c_function.is_user_mentor.restype = ctypes.c_bool

# save_class_info 함수 정의
c_function.save_class_info.argtypes = [ctypes.c_char_p] * 8
c_function.save_class_info.restype = ctypes.c_bool

# apply_class_in_c 함수 정의
c_function.apply_class_in_c.argtypes = [ctypes.c_char_p]
c_function.apply_class_in_c.restype = ctypes.c_bool

# change_id 함수 설정
c_function.change_id.restype = ctypes.c_bool
c_function.change_id.argtypes = [ctypes.c_char_p]

# change_password 함수 설정
c_function.change_password.restype = ctypes.c_bool
c_function.change_password.argtypes = [ctypes.c_char_p]

# -----------------------------정인성 ----------------------------
# admin페이지에서 보여줄 내용 (회원가입 대기자) 저장하는 리스트
signup_data = []

# 로그인 페이지 -> 실행되면 login.html 실행
@app.route('/')
def login_page():
    return render_template('login.html')

# 로그인 시도 받으면 처리하는 라우트
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data['id'].encode('utf-8')
    user_password = data['password'].encode('utf-8')
    
    # login_rst > 2: admin, 1: 일반 사용자, 0: 오류, -1: 승인 대기중, -2: 거절
    login_rst = c_function.login(user_id, user_password)
    
    if login_rst == 2:
        session['admin'] = True
        return jsonify({"success": True, "redirect": "/admin"}) # admin페이지로 이동
    elif login_rst == 1:
        session['user_id'] = user_id  # 세션에 user_id 저장
        session['user_password'] = user_password # 세션에 비밀번호 저장
        return jsonify({"success": True, "redirect": "/main"}) # main페이지로 이동
    elif login_rst == -1:
        return jsonify({"success": False, "message": "관리자 승인 대기중입니다."})
    elif login_rst == -2:
        session['rejected_user'] = data['id']
        return jsonify({"success": False, "message": "회원가입이 거절되었습니다."})

    return jsonify({"success": False, "message": "아이디 또는 비밀번호가 잘못되었습니다."})

# 회원가입 처리하는 라우트
@app.route('/sign_up.html', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'GET':
        return render_template('sign_up.html')
    
    try:
        # 사용자 정보 저장
        user_id = request.form['id']
        user_password = request.form['password']
        user_status = 'pending' # 회원가입 진행 상태 나타내는 정보. 기본적으로 pendig : 대기중
        user_role = request.form['role'] # mento 또는 mentee
        user_name = request.form['name']
        user_birthday = request.form['birthday']
        user_gender = request.form['gender']

        uploaded_files = [] # 업로드된 파일 모으는 리스트
        for file in request.files.getlist('files'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            uploaded_files.append(file_path)

        # 회원가입 대기 상태로 전환
        result = c_function.signup_request(
            user_id.encode('utf-8'), 
            user_password.encode('utf-8'), 
            user_status.encode('utf-8'),
            user_role.encode('utf-8'),
            user_name.encode('utf-8'), 
            user_birthday.encode('utf-8'),
            user_gender.encode('utf-8')
        )

        # 사용자가 업로드한 파일을 압축 => admin페이지에서 다운받아서 확인 가능
        zip_filename = f"{user_id}_files.zip"
        zip_path = os.path.join(USER_INFO_FOLDER, zip_filename)
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            txt_file_path = os.path.join(USER_INFO_FOLDER, f"{user_id}_info.txt")
            zipf.write(txt_file_path, os.path.basename(txt_file_path))
            for file_path in uploaded_files:
                zipf.write(file_path, os.path.basename(file_path))

        signup_data.append({
            'id': user_id,
            'apply_date': time.strftime("%Y.%m.%d"),
            'role': user_role,
            'zip_path': zip_path
        })
        return jsonify({"success": result})
    
    except Exception as e:
        print(f"오류 발생: {e}")
        return jsonify({"success": False, "message": f"서버 오류: {str(e)}"})

# 회원가입 수락하는 라우트
@app.route('/signup_accept/<user_id>', methods=['POST'])
def accept_signup(user_id):
    # signup_fuction은 status를 approved로 변경. 성공하면 true, 실패하면 false
    result = c_function.signup_accept(user_id.encode('utf-8'))
    if result:
        global signup_data
        # 회원가입 대기자 명단에서 회원가입 수락된 사람 제거
        signup_data = [x for x in signup_data if x['id'] != user_id]
        return jsonify({"success": True})
    return jsonify({"success": False})

# 회원가입 거절하는 라우트
@app.route('/signup_reject/<user_id>', methods=['POST'])
def reject_signup(user_id):
    # status를 rejected로 변경
    result = c_function.signup_reject(user_id.encode('utf-8'))
    if result:
        global signup_data
        # 회원가입 대기자 명단에서 회원가입 거절된 사람 제거
        signup_data = [signup for signup in signup_data if signup['id'] != user_id]
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/delete_rejected_user', methods=['POST'])
def confirm_rejection():
    # 세션에서 거절된 사용자 ID를 가져옴
    user_id = session.pop('rejected_user', None)
    
    if user_id:
        # delete_user 함수로 사용자의 모든 정보 삭제
        result = c_function.delete_user(user_id.encode('utf-8'))  # 해당 ID에 대한 정보 삭제
        if result:
            return jsonify({"success": True})
    
    return jsonify({"success": False})

# 아이디 중복 확인 라우트
@app.route('/check_duplicate', methods=['POST'])
def check_duplicate():
    user_id = request.json['id'].encode('utf-8')
    is_duplicate = c_function.duplicate_check(user_id)
    return jsonify({"is_duplicate": is_duplicate})

# admin페이지에서 사용자 정보, 제출 서류를 모은 zip파일 다운받는 라우트
@app.route('/download_zip/<user_id>')
def download_zip(user_id):
    user_zip_path = None
    for x in signup_data:
        if x['id'] == user_id:
            user_zip_path = x['zip_path']
            break  # 첫 번째로 조건을 만족하는 항목을 찾으면 루프 종료

    if user_zip_path and os.path.exists(user_zip_path):
        return send_file(user_zip_path, as_attachment=True, download_name=f"{user_id}_files.zip", mimetype='application/zip')
    return "파일을 찾을 수 없습니다.", 404

# admin페이지 라우트
@app.route('/admin')
def admin_page():
    signup_data.clear()  # 기존 데이터를 초기화
    
    # CSV 파일에서 대기열 사용자 데이터 읽기
    try:
        with open('static/user.csv', 'r', encoding='UTF-8') as file:
            for line in file:
                user_info = line.strip().split(',')
                if len(user_info) < 7:
                    continue
                
                id, pw, status, role, name, birthday, gender = user_info
                
                # 'pending' 상태인 사용자만 대기열에 추가
                if status == 'pending':
                    signup_data.append({
                        'id': id,
                        'apply_date': time.strftime("%Y.%m.%d"), 
                        'role': role,
                        'zip_path': f'static/users/{id}_files.zip'  # 파일 경로 설정
                    })
    except FileNotFoundError:
        print("user.csv 파일을 찾을 수 없습니다.")

    return render_template('admin.html', signup_data=signup_data)

# admin페이지 로그아웃 라우트
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('login_page'))

@app.route('/user_logout')
def user_logout():
    session.pop('user_id', None)
    session.pop('user_password', None)
    return redirect(url_for('login_page'))

# ----------------------------- 임수빈 ----------------------------

def is_user_mentor(user_id):
    # user_id가 str 타입이면 encode()를 호출하여 bytes로 변환
    if isinstance(user_id, str):
        user_id = user_id.encode('utf-8')
    
    # 이후 C 함수 호출
    return c_function.is_user_mentor(user_id)


# save_class_info 함수 불러오기
def save_class_in_c(class_title, mentor_name, location, class_description, price, mode, capacity, image_path):
    class_title_bytes = class_title.encode('utf-8')
    mentor_name_bytes = mentor_name.encode('utf-8')
    location_bytes = location.encode('utf-8')
    class_description_bytes = class_description.encode('utf-8')
    price_bytes = price.encode('utf-8')
    mode_bytes = mode.encode('utf-8')
    capacity_bytes = capacity.encode('utf-8')
    image_path_bytes = image_path.encode('utf-8')
    return c_function.save_class_info(class_title_bytes, mentor_name_bytes, location_bytes, 
                               class_description_bytes, price_bytes, mode_bytes, capacity_bytes, image_path_bytes) # C 함수 호출

def load_classes_from_c():
    classes = []
    try:
        with open('static/classes.csv', 'r', encoding='utf-8') as csvfile:
            for line in csvfile:
                fields = line.strip().split(',')
                if len(fields) == 10:  # 필드 개수 확인
                    # 클래스 정보를 딕셔너리 형태로 추가
                    class_title, mentor_name, location, class_description, price, mode, capacity, current_applicants, image_path, tags = fields
                    classes.append({
                        'class_title': class_title,
                        'mentor_name': mentor_name,
                        'location': location,
                        'class_description': class_description,
                        'price': price,
                        'mode': mode,
                        'capacity': int(capacity),
                        'current_applicants': int(current_applicants),
                        'image_path': image_path,
                        'tags': tags
                    })
    except FileNotFoundError:
        pass  # 파일이 없을 경우 예외 처리

    return classes

# 메인 페이지
@app.route('/main')
def main():
    classes = load_classes_from_c()  # csv 파일에서 클래스 정보 불러오기
    role = session.get('role', 'mentee')  # 현재 로그인된 사용자의 역할 확인
    return render_template('main.html', classes=classes, user_role=role)

@app.route('/class_page')
def class_page():
    classes = load_classes_from_c()  # csv 파일에서 클래스 정보 불러오기
    role = session.get('role', 'mentee')  # 현재 로그인된 사용자의 역할 확인
    return render_template('class.html', classes=classes, user_role=role)

@app.route('/check_mentor')
def check_mentor():
    user_id = session.get('user_id')  # 세션에서 사용자 아이디를 가져옵니다.
    
    # 세션에 user_id가 없으면 로그인 페이지로 리다이렉트
    if not user_id:
        return redirect(url_for('login'))  # 'login'은 로그인 페이지를 처리하는 함수명입니다.
    
    # 멘토 여부 확인
    if is_user_mentor(user_id):
        print("pmentor")
        return {'status': 'mentor'}
    else:
        print("pmentee`")
        return {'status': 'mentee'}
    
# 클래스 생성 페이지로 이동
@app.route('/create_class', methods=['GET'])
def create_class_form():
    return render_template('create_class.html')

# 클래스 생성 요청 처리
@app.route('/create_class', methods=['POST'])
def create_class():
    # 클래스 정보 추출
    class_title = request.form['class_title']
    mentor_name = request.form['mentor_name']
    location = request.form['location']
    class_description = request.form['class_description']
    price = request.form['price']
    mode = request.form['mode']
    capacity = request.form['capacity']
    tags = request.form['tags']
    image = request.files['class_image']

    # 이미지 저장 경로 설정 & 저장
    image_filename = image.filename
    image_path = os.path.join('images/class_image', image_filename).replace("\\", "/")
    image.save(os.path.join('static', image_path))

    current_applicants = 0  # 신청 인원 초기값 0으로 설정

    # csv 파일에 새 클래스 추가
    with open('static/classes.csv', 'a', encoding='utf-8') as csvfile:
        csvfile.write(f"{class_title},{mentor_name},{location},{class_description},"
                      f"{price},{mode},{capacity},{current_applicants},{image_path},{tags}\n")

    return redirect(url_for('main'))

# 특정 클래스의 세부 정보 표시
@app.route('/class_details/<class_title>', methods=['GET'])
def class_details(class_title):
    class_details = {}
    class_details_str = ctypes.create_string_buffer(1024)

    success = c_function.load_class_details(class_title.encode('utf-8'), class_details_str)  # C 함수 호출
    if success:
        details = class_details_str.value.decode('utf-8').strip().split(',')
        if len(details) == 10:
            # 각 필드를 딕셔너리에 저장 -> 템플릿에 전달
            class_details = {
                'class_title': details[0],
                'mentor_name': details[1],
                'location': details[2],
                'class_description': details[3],
                'price': details[4],
                'mode': details[5],
                'capacity': int(details[6]),
                'current_applicants': int(details[7]) if details[7] is not None else 0,
                'image_path': details[8],
                'tags': details[9]
            }
    else:
        return "클래스를 찾을 수 없습니다.", 404
    return render_template('class_details.html', class_details=class_details)

# 특정 클래스에 사용자가 신청할 때 호출
@app.route('/apply_class/<class_title>', methods=['POST'])
def apply_class(class_title):
    applicant_name = request.form['applicant_name']
    applicant_id = request.form['applicant_id']
    email = request.form['email']

    # applications.csv에 신청 정보 저장
    with open('static/applications.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([class_title, applicant_id, applicant_name, email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

    # C 함수 호출로 신청 처리
    class_title_bytes = class_title.encode('utf-8')
    success = c_function.apply_class_in_c(class_title_bytes)  # C 함수 호출

    # 신청이 성공하면 상세 페이지로 이동, 실패하면 오류 메시지 전달
    if success:
        return render_template('class.html', classes=load_classes_from_c(), success_message="신청이 완료되었습니다")
    else:
        return redirect(url_for('class_page', error="신청 인원이 초과되었습니다.")), 400

# ----------------------------- 정세은 ----------------------------
@app.route('/get_user_info', methods=['GET'])
def get_user_info():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "User not logged in"}), 401

    user_info = {
        "id": user_id.decode('utf-8'),  # 바이트형식에서 문자열로 변환
        #"subtitle": "베이킹 꿈나무"  # 이 부분은 실제 DB에서 가져오는 값을 사용해야 합니다.
    }
    return jsonify(user_info)

@app.route('/get_user_info_simple', methods=['GET'])
def get_user_info_simple():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "User not logged in"}), 401

    user_info = {
        "id": user_id.decode('utf-8'),  # 바이트형식에서 문자열로 변환
        #"subtitle": "베이킹 꿈나무"  # 이 부분은 실제 DB에서 가져오는 값을 사용해야 합니다.
    }
    return jsonify(user_info)

@app.route('/mypage')
def mypage():
    if 'user_id' not in session:
        return render_template('login.html', message="올바르지 못한 접근입니다.")

    user_id = session['user_id'].decode('utf-8')  # 세션에서 사용자 ID 가져오기
    enrolled_classes = []

    # applications.csv에서 현재 사용자와 관련된 클래스 정보를 읽기
    try:
        with open('static/applications.csv', 'r', encoding='utf-8') as csvfile: 
            reader = csv.reader(csvfile)
            for row in reader:
                class_title, applicant_id, applicant_name, email, apply_time = row
                if applicant_id == user_id:
                    enrolled_classes.append(class_title)
    except FileNotFoundError:
        pass  # 파일이 없으면 빈 리스트 유지

    # 모든 클래스 정보 로드 후 필터링
    all_classes = load_classes_from_c()  # 모든 클래스 정보를 로드
    filtered_classes = [
        cls for cls in all_classes if cls['class_title'] in enrolled_classes
    ]

    return render_template('mypage.html', classes=filtered_classes)




# 마이페이지-고객센터 라우트
@app.route('/help')
def help():
    return render_template('help.html')  # help.html 렌더링

# 마이페이지-프로필수정 라우트
@app.route('/picture_change')
def picture_change():
    return render_template('picture_change.html')

@app.route('/update-profile-picture', methods=['POST'])
def update_profile_picture():
    data = request.json
    photo = data.get('photo')
    user_id = session.get('user_id')  # 세션에서 사용자 ID 가져오기

    if not user_id:
        return jsonify(success=False, message="User not logged in")

    if photo:
        # 세션에 프로필 사진 경로 저장
        session['profile_pic'] = photo
        return jsonify(success=True, message="프로필 사진이 성공적으로 변경되었습니다.")
    
    return jsonify(success=False, message="사진 정보가 없습니다.")



@app.route('/get-profile-picture', methods=['GET'])
def get_profile_picture():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify(success=False, message="User not logged in")

    # 세션에서 프로필 사진 경로 가져오기
    photo = session.get('profile_pic', '/static/images/profile/default.png')  # 기본값 제공
    return jsonify(success=True, photo=photo)


@app.route('/change_id', methods=['POST'])
def change_id():
    data = request.json
    new_id = data.get('new_id')  # JSON 데이터에서 new_id 가져오기
    old_id = session.get('user_id')  # 세션에서 user_id 가져오기

    # 검증
    if not old_id:
        return jsonify({"success": False, "message": "Session user_id is missing"})
    if not new_id or not isinstance(new_id, str):
        return jsonify({"success": False, "message": "Invalid new ID"})

    # ID 변경 로직 호출
    result = c_function.change_id(old_id, new_id.encode('utf-8')) # 세션에서 가져온애들은 이미 인코드 했기 때문에 다시 하면 안됨. new_id만 해주기

    if result:
        session.pop('user_id', None)  # 세션에서 삭제 (로그아웃)
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Failed to change ID"})


@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.json
    user_id = session.get('user_id')  # 세션에서 user_id 가져오기
  # JSON 데이터에서 id 가져오기
    old_password = session.get('user_password')  # JSON 데이터에서 oldPassword 가져오기 아니고 마찬가지로 user_password세션에서 가져와야 함.
    new_password = data.get('newPassword')  # JSON 데이터에서 newPassword 가져오기

    # 검증
    if not user_id or not old_password or not new_password:
        return jsonify({"success": False, "message": "Invalid input"})

    # 비밀번호 변경 로직 호출
    result = c_function.change_password(user_id, old_password, new_password.encode('utf-8'))

    if result:
        session.pop('user_id', None)  # 세션에서 삭제 (로그아웃)
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Failed to change password"})

if __name__ == '__main__':
    app.run(debug=True)


