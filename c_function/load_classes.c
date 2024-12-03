#define _CRT_SECURE_NO_WARNINGS
#include "user.h"
#include "class_management.h" // Ŭ���� ������ ���õ� �Լ�, ����� ������ ��� ���� ���� ����.

// CSV ���Ͽ��� Ŭ���� ����� �ҷ����� �Լ�
bool load_classes(const char* filename, char classes[][1024], int* count) {
    FILE* file = fopen(filename, "r"); // ������ �б� ���� ����
    if (file == NULL) { // ������ ������ ������ ���� �޽��� ��� �� �Լ� ����
        printf("Ŭ���� ������ �ҷ��� �� �����ϴ�.\n");
        return false;
    }

    char line[MAX_LINE_LENGTH]; // ���Ͽ��� �� �پ� �о�� �迭 ����
    *count = 0; // Ŭ���� ������ 0���� �ʱ�ȭ
    while (fgets(line, sizeof(line), file)) { // ���Ͽ��� �� �پ� �б�
        // �� ������ ������ ���� ����
        char class_title[100], mentor_name[100], location[100], class_description[500];
        char price[20], mode[20], capacity[10], current_applicants[10], image_path[200];

        // �������� ��ǥ�� �����Ͽ� ������ ������ ����
        if (sscanf(line, "%99[^,],%99[^,],%99[^,],%499[^,],%19[^,],%19[^,],%9[^,],%9[^,],%199[^\n]",
            class_title, mentor_name, location, class_description, price, mode, capacity, current_applicants, image_path) == 9) {
            // �� �ʵ带 ���ڿ� �������� �迭�� ����
            snprintf(classes[*count], sizeof(line), "%s,%s,%s,%s,%s,%s,%s,%s,%s",
                class_title, mentor_name, location, class_description, price, mode, capacity, current_applicants, image_path);
            (*count)++; // Ŭ���� ���� ����
        }
    }

    fclose(file); // ���� �ݱ�
    return true; // ���������� �о����� ��ȯ
}
