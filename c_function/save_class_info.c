#define _CRT_SECURE_NO_WARNINGS 
#include "user.h"
#include "class_management.h" // Ŭ���� ������ ���õ� �Լ�, ����� ������ ��� ���� ���� ����.

// Ŭ���� ������ CSV ���Ͽ� �����ϴ� �Լ�
bool save_class_info(const char* class_title, const char* mentor_name, const char* location, const char* class_description, const char* price, const char* mode, const char* capacity, const char* image_path) {
    // ������ �߰� ���� ����
    FILE* file = fopen("static/classes.csv", "a");
    if (file == NULL) { // ������ ������ ������ ���� �޽��� ��� �� �Լ� ����
        printf("Ŭ���� ������ ������ �� �����ϴ�.\n");
        return false;
    }

    // image_path���� ��θ� '/'�� �����ϵ����Ͽ�, ������ �ν� ������ ��η� ����
    char formatted_image_path[200];
    snprintf(formatted_image_path, sizeof(formatted_image_path), "%s", image_path);
    for (int i = 0; formatted_image_path[i] != '\0'; i++) {
        if (formatted_image_path[i] == '\\') { // '\' -> '/'�� ����
            formatted_image_path[i] = '/';
        }
    }

    // CSV ���Ͽ� Ŭ���� ���� �ۼ�(�ʱ� �ο� 0���� ����)
    fprintf(file, "%s,%s,%s,%s,%s,%s,%s,0,%s\n", class_title, mentor_name, location, class_description, price, mode, capacity, formatted_image_path);
    fclose(file);
    return true;
}
