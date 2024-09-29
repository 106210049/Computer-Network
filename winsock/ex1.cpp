#include <iostream>
#include <winsock2.h>

//  g++ tên_file.cpp -o tenfile.exe -lws2_32
// ./ tên_file.exe
using namespace std;
int main()
{
    // cout << "Hello world" << endl;
    WSADATA wsaData;
    WORD wVersion = MAKEWORD(2, 2);
    int Stat;
    if ((Stat == WSAStartup(wVersion, &wsaData)) != 0)
    {
        cout << "Startup winsock failed with error" << Stat << endl;
        return 0;
    }
    else
    {
        cout << "Startup winsock completed successfully ...";
    }
    if (WSACleanup() == SOCKET_ERROR)
    {
        cout << "WSACleanup failed with error" << WSAGetLastError() << endl;
    }
    return 0;
}