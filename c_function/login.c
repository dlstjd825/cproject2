// �α���
#include "user.h"

__declspec(dllexport) int login(const char* ID, const char* PW) {
    // �� �޸𸮿� User �迭 �Ҵ�
    User* users = (User*)malloc(MAX_USERS * sizeof(User));
    if (users == NULL) {
        printf("Memory allocation failed.\n");
        return 0;  // �޸� �Ҵ� ���� �� �α��� ���з� ��ȯ
    }

    int num_users = load_users(users, MAX_USERS);

    // User �迭�� ID �������� ����
    qsort(users, num_users, sizeof(User), compare_users);

    // ���� Ž������ ID ã��
    int index = binary_search(users, 0, num_users - 1, ID);

    int result = 0;  // �⺻ �α��� ���� ����
    if (index != -1 && strcmp(users[index].pw, PW) == 0) {
        // ������� ���� Ȯ��
        if (strcmp(users[index].status, "approved") == 0) {
            result = strcmp(ID, "admin") == 0 ? 2 : 1;  // �α��� ���� (������ �Ǵ� �Ϲ� �����)
        }
        else if (strcmp(users[index].status, "pending") == 0) {
            result = -1;  // ���� ��� ���� �����
        }
        else if (strcmp(users[index].status, "rejected") == 0) {
            result = -2;  // ������ �����
        }
    }

    free(users);  // �޸� ����
    return result;
}


