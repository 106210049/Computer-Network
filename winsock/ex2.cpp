#include <iostream>
#include <winsock2.h>
#include <WS2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

using namespace std;

int main()
{
    WSADATA wsaData;
    WORD wVersion = MAKEWORD(2, 2);
    int Stat;

    // Initialize Winsock
    Stat = WSAStartup(wVersion, &wsaData);
    if (Stat != 0)
    {
        cout << "Startup winsock failed with error: " << Stat << endl;
        return 1;
    }
    else
    {
        cout << "Startup winsock completed successfully ..." << endl;
    }

    char ip[] = "127.0.0.";
    char stCodeString[10];
    unsigned int stCode = 106210049;
    unsigned int number = (stCode % 255) + 1;
    sprintf(stCodeString, "%d", number);
    strcat(ip, stCodeString);
    cout << "IP address: " << ip << endl;

    // inet_addr function
    unsigned long ip_addr1 = inet_addr(ip);
    if (ip_addr1 == INADDR_NONE)
    {
        cout << "Can't convert IP by inet_addr\n"
             << endl;
    }
    else
    {
        cout << "Convert inet_addr completed: " << ip_addr1 << endl;
    }

    // inet_pton
    struct in_addr ip_addr2;
    int result = inet_pton(AF_INET, ip, &ip_addr2);
    if (result == 1)
    {
        cout << "Convert inet_pton completed: " << ip_addr2.s_addr << endl;
    }
    else if (result == 0)
    {
        cout << "inet_pton failed: invalid address format\n";
    }
    else
    {
        cout << "inet_pton failed with error\n";
    }

    // Cleanup Winsock
    if (WSACleanup() == SOCKET_ERROR)
    {
        cout << "WSACleanup failed with error: " << WSAGetLastError() << endl;
    }

    return 0;
}
