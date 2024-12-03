//���̵� �ߺ� üũ
#include "user.h"

// �ߺ� Ȯ�� �Լ�
__declspec(dllexport) bool duplicate_check(const char* id) {
    User* users = (User*)malloc(MAX_USERS * sizeof(User));
    if (users == NULL) {
        // �޸� �Ҵ� ���� ó��
        return false;
    }

    int num_users = load_users(users, MAX_USERS);

    // ���� (�ʿ��� ���)
    qsort(users, num_users, sizeof(User), compare_users);

    // ���� Ž������ �ߺ� ���� Ȯ��
    bool result = binary_search(users, 0, num_users - 1, id) == -1 ? false : true;

    // �޸� ����
    free(users);

    return result;
}

