#define _CRT_SECURE_NO_WARNINGS
#include "user.h"
#include "class_management.h" // Ŭ���� ������ ���õ� �Լ�, ����� ������ ��� ���� ���� ����.

// Ư�� Ŭ������ ��û�ϰ� ��û �ο��� ������Ʈ�ϴ� �Լ�
__declspec(dllexport) bool apply_class_in_c(const char* class_title) {
    // csv ������ �б� �� ���� ���� ����
    FILE* file = fopen("static/classes.csv", "r+");
    if (file == NULL) { // ������ ������ ������ ���� �޽��� ��� �� �Լ� ����
        printf("Ŭ���� ������ ������ ������ �� �� �����ϴ�.\n");
        return false;
    }

    char line[MAX_LINE_LENGTH];
    char updated_content[10000] = ""; // ������ ���� ������ ������ ���ڿ�
    bool found_class = false; // Ŭ������ �߰ߵǾ����� ���θ� ��Ÿ��

    // ���Ͽ��� �� �پ� �б�
    while (fgets(line, sizeof(line), file)) {
        // �� Ŭ���� ������ ������ ������ ����
        char current_title[100], mentor_name[100], location[100], description[500];
        char price[20], mode[20], capacity[10], current_applicants[10], image_path[200];

        // ��ǥ�� ���е� �� ������ �о�� ������ ����
        if (sscanf(line, "%99[^,],%99[^,],%99[^,],%499[^,],%19[^,],%19[^,],%9[^,],%9[^,],%199[^\n]",
            current_title, mentor_name, location, description, price, mode, capacity, current_applicants, image_path) == 9) {

            // ã�� �ִ� Ŭ���� ����� ��ġ�ϴ��� Ȯ��
            if (strcmp(class_title, current_title) == 0) {
                int current_applicants_num = atoi(current_applicants); // ���� ��û �ο��� ������ ��ȯ
                int capacity_num = atoi(capacity); // �ִ� ���� �ο��� ������ ��ȯ

                // ��û �ο��� �ִ� ���� �ο��� �ʰ��ϴ��� Ȯ��
                if (current_applicants_num >= capacity_num) {
                    fclose(file);
                    return false;
                }

                // ��û �ο� +1
                current_applicants_num++;
                snprintf(current_applicants, sizeof(current_applicants), "%d", current_applicants_num); // ������ �ο� ����
                found_class = true; // Ŭ������ �߰ߵǾ����� ǥ��
            }

            // ���� ���� ������ ���·� ����
            char updated_line[MAX_LINE_LENGTH];
            snprintf(updated_line, sizeof(updated_line), "%s,%s,%s,%s,%s,%s,%s,%s,%s\n",
                current_title, mentor_name, location, description, price, mode, capacity, current_applicants, image_path);
            strcat(updated_content, updated_line); // ������ ���� ��ü ������Ʈ�� ���뿡 �߰�
        }
    }

    fclose(file);

    // ������Ʈ�� ������ ���Ͽ� �ٽ� �ۼ�
    if (found_class) {
        file = fopen("static/classes.csv", "w"); // ������ ���� ���� �ٽ� ����
        if (file == NULL) { // ������ ������ ������ ���� �޽��� ��� �� �Լ� ����
            printf("Ŭ���� ������ ������ ������ �� �� �����ϴ�.\n");
            return false;
        }
        fputs(updated_content, file); // ������ ���� ���Ͽ� �ۼ�
        fclose(file);
    }

    return found_class; // Ŭ������ ã������ true, ã�� �������� false ��ȯ
}
