#define _CRT_SECURE_NO_WARNINGS
#include "user.h"
#include "class_management.h" // 클래스 관리와 관련된 함수, 상수를 포함한 헤더 파일 따로 정리.

// 사용자가 멘토인지 여부를 확인하는 함수
__declspec(dllexport) bool is_user_mentor(const char* user_id) {
    // 사용자 정보 파일을 읽기 모드로 열기
    FILE* file = fopen("static/user.csv", "r");
    if (file == NULL) { // 파일이 열리지 않으면 오류 메시지 출력 후 기본값 false 반환
        printf("사용자 정보를 저장한 파일을 열 수 없습니다.\n");
        return false;
    }

    char line[MAX_LINE_LENGTH];
    char csv_user_id[50];       // csv에서 읽은 사용자 id 저장
    char csv_status[20];        // csv에서 읽은 상태(pending, approved 등) 저장
    char csv_role[20];          // csv에서 읽은 역할(mentor 혹은 mentee) 저장

    // csv 파일에서 한 줄씩 읽기
    while (fgets(line, sizeof(line), file)) {
        // 각 줄에서 사용자 id, 역할을 추출
        if (sscanf(line, "%49[^,],%*[^,],%*[^,],%19[^,],%*[^,],%*[^,],%*[^,]", csv_user_id, csv_role) == 2) {
            // 사용자 id가 일치하고 mentor인지 확인
            if (strcmp(user_id, csv_user_id) == 0 && strcmp(csv_role, "mentor") == 0) {
                fclose(file);
                return true;
            }
        }
    }

    fclose(file);
    return false;
}
