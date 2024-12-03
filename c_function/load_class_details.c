#define _CRT_SECURE_NO_WARNINGS
#include "user.h"
#include "class_management.h" // Ŭ���� ������ ���õ� �Լ�, ����� ������ ��� ���� ���� ����.

// Ư�� Ŭ���� ������ ������� csv ���Ͽ��� �ش� Ŭ������ ���� ������ ã�� �Լ�
bool load_class_details(const char* class_title, char* class_details) {
    // CSV ������ �б� ���� ����
    FILE* file = fopen("static/classes.csv", "r");
    if (file == NULL) { // ������ ������ ������ ���� �޽��� ��� �� �Լ� ����
        printf("Ŭ���� ������ �ҷ��� �� �����ϴ�.\n");
        return false;
    }

    char line[1024];
    while (fgets(line, sizeof(line), file)) { // ���Ͽ��� �� �پ� �б�
        // ���� �ٿ� Ư�� Ŭ���� ������ ���ԵǾ� �ִ��� Ȯ��
        if (strstr(line, class_title) != NULL) {
            // class_details(����� ���̽� �Լ�!)�� Ŭ���� ������ ��� �ش� �� ����
            strcpy(class_details, line);
            fclose(file); // ���� �ݱ�
            return true;
        }
    }

    fclose(file); // ������ �� ���� �� �ݱ�
    return false;
}
