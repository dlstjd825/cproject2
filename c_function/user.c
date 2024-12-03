// user.h ������� �Լ� ����
#define _CRT_SECURE_NO_WARNINGS
#include "user.h"

// ����ڸ� id������ ������ �Լ�
int compare_users(const void* a, const void* b) {
    return strcmp(((User*)a)->id, ((User*)b)->id);
}

// ���� Ž�� �Լ�: ���ĵ� users �迭���� id�� ã��
int binary_search(User* users, int left, int right, const char* id) {
    while (left <= right) {
        int mid = left + (right - left) / 2;
        int cmp = strcmp(id, users[mid].id);

        if (cmp == 0) { // ID�� ��ġ�ϴ� ���
            return mid;  // ��ġ�ϴ� �ε��� ��ȯ
        }
        else if (cmp < 0) {
            right = mid - 1;
        }
        else {
            left = mid + 1;
        }
    }   
    return -1;  // ID�� ���� ���
}

// ����ڸ� user.csv���� �ҷ���
int load_users(User* users, int max_users) {
    FILE* file = fopen("static/user.csv", "r");
    if (file == NULL) {
        perror("Failed to open CSV file");
        return 0;
    }

    int count = 0;
    char line[MAX_LINE_LENGTH];

    while (fgets(line, sizeof(line), file) && count < max_users) {
        // �� �ٿ��� ��� �ʵ带 �����Ͽ� User �迭�� ����
        if (sscanf(line, "%49[^,],%49[^,],%9[^,],%9[^,],%49[^,],%49[^,],%1s",
            users[count].id, users[count].pw, users[count].status,
            users[count].role, users[count].name, users[count].birthday, users[count].gender) == 7) {
            // �� �ʵ忡 ���� ���� ���� ����
            trim_newline(users[count].id);
            trim_newline(users[count].pw);
            trim_newline(users[count].status);
            trim_newline(users[count].role);
            trim_newline(users[count].name);
            trim_newline(users[count].birthday);
            trim_newline(users[count].gender);

            count++;
        }
    }

    fclose(file);
    return count;  // �ε�� ����� �� ��ȯ
}

// ���ڿ����� �����Լ� ����
void trim_newline(char* str) {
    str[strcspn(str, "\n")] = '\0';
}

