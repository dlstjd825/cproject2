#define _CRT_SECURE_NO_WARNINGS
#include "user.h"
#include "class_management.h" // Ŭ���� ������ ���õ� �Լ�, ����� ������ ��� ���� ���� ����.

// ����ڰ� �������� ���θ� Ȯ���ϴ� �Լ�
__declspec(dllexport) bool is_user_mentor(const char* user_id) {
    // ����� ���� ������ �б� ���� ����
    FILE* file = fopen("static/user.csv", "r");
    if (file == NULL) { // ������ ������ ������ ���� �޽��� ��� �� �⺻�� false ��ȯ
        printf("����� ������ ������ ������ �� �� �����ϴ�.\n");
        return false;
    }

    char line[MAX_LINE_LENGTH];
    char csv_user_id[50];       // csv���� ���� ����� id ����
    char csv_status[20];        // csv���� ���� ����(pending, approved ��) ����
    char csv_role[20];          // csv���� ���� ����(mentor Ȥ�� mentee) ����

    // csv ���Ͽ��� �� �پ� �б�
    while (fgets(line, sizeof(line), file)) {
        // �� �ٿ��� ����� id, ������ ����
        if (sscanf(line, "%49[^,],%*[^,],%*[^,],%19[^,],%*[^,],%*[^,],%*[^,]", csv_user_id, csv_role) == 2) {
            // ����� id�� ��ġ�ϰ� mentor���� Ȯ��
            if (strcmp(user_id, csv_user_id) == 0 && strcmp(csv_role, "mentor") == 0) {
                fclose(file);
                return true;
            }
        }
    }

    fclose(file);
    return false;
}
