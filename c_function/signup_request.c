// ȸ������ ��û
#include "user.h"

__declspec(dllexport) bool signup_request(const char* ID, const char* PW, const char* status, const char* role, const char* name, const char* birthday, const char* gender) {
    char txt_filename[256];
    snprintf(txt_filename, sizeof(txt_filename), "static/users/%s_info.txt", ID);

    // txt���� �ۼ� : �����ڰ� ����� ���� Ȯ�ο뵵
    FILE* txt_file = fopen(txt_filename, "w");
    if (txt_file == NULL) {
        printf("Failed to create user info file\n");
        return false;
    }

    // ����� ������ �ؽ�Ʈ ���Ͽ� �ۼ�
    fprintf(txt_file, "ID: %s\nPW: %s\nStatus: %s\nRole: %s\nName: %s\nBirthday: %s\nGender: %s\n",
        ID, PW, status, role, name, birthday, gender);
    fclose(txt_file);

    // user.csv ���Ͽ� ����� ���� �߰�
    FILE* csv_file = fopen("static/user.csv", "a+");
    if (csv_file == NULL) {
        perror("Failed to open CSV file");
        return false;
    }

    // user.csv���� ���ο� ������ �� �������� �߰��� �� �ֵ��� ��
    fseek(csv_file, 0, SEEK_END);

    // CSV �������� ����� ������ �߰�
    fprintf(csv_file, "%s,%s,%s,%s,%s,%s,%s\n", ID, PW, status, role, name, birthday, gender);
    fclose(csv_file);

    return true;
}


