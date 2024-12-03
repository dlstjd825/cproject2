#define _CRT_SECURE_NO_WARNINGS
#include "user.h"

__declspec(dllexport) bool change_id(const char* old_id, const char* new_id) {
    // �� �޸𸮿� User �迭 �Ҵ�
    User* users = (User*)malloc(MAX_USERS * sizeof(User));
    if (users == NULL) {
        printf("Memory allocation failed.\n");
        return false;
    }

    int num_users = load_users(users, MAX_USERS);

    if (num_users == 0) {
        printf("No users loaded.\n");
        free(users); // �޸� ����
        return false;
    }

    // User �迭�� ID �������� ����
    qsort(users, num_users, sizeof(User), compare_users);

    // ���� ���̵� �ִ��� Ȯ��
    int index = binary_search(users, 0, num_users - 1, old_id);
    if (index == -1) {
        printf("User not found.\n");
        free(users); // �޸� ����
        return false;
    }

    // �� ���̵� �ߺ��Ǵ��� Ȯ��
    if (binary_search(users, 0, num_users - 1, new_id) != -1) {
        printf("New ID already exists.\n");
        free(users); // �޸� ����
        return false;
    }

    // ���̵� ����
    strcpy(users[index].id, new_id);

    // ����� ����� ������ CSV ���Ͽ� �ٽ� ����
    FILE* csv_file = fopen("static/user.csv", "w");
    if (!csv_file) {
        perror("Failed to open CSV file for writing");
        free(users); // �޸� ����
        return false;
    }

    for (int i = 0; i < num_users; i++) {
        fprintf(csv_file, "%s,%s,%s,%s,%s,%s,%s\n",
            users[i].id, users[i].pw, users[i].status,
            users[i].role, users[i].name, users[i].birthday, users[i].gender);
    }

    fclose(csv_file);
    free(users); // �޸� ����

    return true;
}
