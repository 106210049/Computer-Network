#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <string>
#include <algorithm> // Thêm thư viện này cho std::replace
// g++ socket_tcp_server.cpp -o socket_tcp_server.exe -lws2_32
// ./socket_tcp_server.exe
using namespace std;

#define SERVER_PORT 5500
#define SERVER_ADDR "127.0.0.1"
#define BUFF_MAXSIZE 1024

#pragma comment(lib, "Ws2_32.lib")
// winsock->set up socket (socket)->bind()->listen()->accept()

int main()
{
    cout << "====== Set up Winsock ======" << endl;
    WSADATA wsaData;
    WORD wVersion = MAKEWORD(2, 2);
    bool Status;

    Status = WSAStartup(wVersion, &wsaData);
    if (Status != 0)
    {
        cout << "Startup winsock failed with error: " << WSAGetLastError() << endl;
        return 1;
    }
    else
    {
        cout << "Startup winsock completed successfully ..." << endl;
    }
    cout << "WSAStartup completed." << endl;

    cout << "====== Set up socket ======" << endl;
    SOCKET listenSock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (listenSock == INVALID_SOCKET)
    {
        cout << "Creating socket failed with code " << WSAGetLastError() << endl;
        WSACleanup(); // Clean up before returning
        return 1;
    }
    cout << "Creating socket completed successfully." << endl;
    sockaddr_in tcpServerAddr;
    tcpServerAddr.sin_family = AF_INET;
    tcpServerAddr.sin_port = htons(SERVER_PORT);
    tcpServerAddr.sin_addr.s_addr = inet_addr(SERVER_ADDR);
    cout << "====== Bind API ======" << endl;
    if (bind(listenSock, (sockaddr *)&tcpServerAddr, sizeof(tcpServerAddr)) == SOCKET_ERROR)
    {
        cout << "Bind API failed with code " << WSAGetLastError() << endl;
        closesocket(listenSock); // Clean up before returning
        WSACleanup();
        return 1;
    }
    cout << "Bind API completed successfully." << endl;
    cout << "====== listen API ======" << endl;
    if (listen(listenSock, 5) == SOCKET_ERROR)
    {
        cout << "Listen failed with code " << WSAGetLastError() << endl;
        closesocket(listenSock); // Clean up before returning
        WSACleanup();
        return 1;
    }
    cout << "Successfully!!! Server is listening for requests..." << endl;
    cout << "========== Accept ==========" << endl;
    sockaddr_in clientAddr;
    char buff[BUFF_MAXSIZE], clientIP[INET_ADDRSTRLEN];
    int ret, clientAddrLen = sizeof(clientAddr), clientPort;

    SOCKET NewConnection = accept(listenSock, (sockaddr *)&clientAddr, &clientAddrLen);
    if (NewConnection == INVALID_SOCKET)
    {
        cout << "Connection failed with code: " << WSAGetLastError() << endl;
        closesocket(listenSock); // Clean up before returning
        WSACleanup();
        return 1;
    }
    inet_ntop(AF_INET, &clientAddr.sin_addr, clientIP, sizeof(clientIP)); // chuyển từ binary sang dạng IP dễ đọc
    clientPort = ntohs(clientAddr.sin_port);                              // chuyển từ binary sang số dễ đọc
    cout << "Connection is established: IP = " << clientIP << " at port = " << clientPort << endl;

    while (1)
    {
        ret = recv(NewConnection, buff, BUFF_MAXSIZE, 0);
        if (ret == SOCKET_ERROR)
        {
            cout << "Error with recv code: " << WSAGetLastError() << endl;
            break;
        }
        else if (ret == 0)
        {
            cout << "Client disconnected. " << endl;
            break;
        }
        else
        {
            buff[ret] = '\0'; // Kết thúc chuỗi nhận được bằng null-terminate

            cout << "Received message from client " << clientIP << ":" << clientPort
                 << ": " << buff << endl;

            // Kiểm tra nếu nhận được lệnh "exit"
            if (strcmp(buff, "exit") == 0)
            {
                cout << "Received exit command from client. Closing connection..." << endl;
                const char *exitMessage = "exit";
                send(NewConnection, exitMessage, strlen(exitMessage), 0);
                break; // Thoát vòng lặp để đóng kết nối
            }
            for (int i = 0; i < sizeof(buff) / sizeof(buff[0]); i++)
            {
                // if (buff[i] >= 'a' && buff[i] <= 'z')
                // {
                //     buff[i] = buff[i] - ('a' - 'A');
                // }
                if (buff[i] >= 'A' && buff[i] <= 'Z')
                {
                    buff[i] = buff[i] - ('A' - 'a');
                }
            }
            // Convert buff to std::string to replace spaces with '_'
            std::string message(buff);

            // Replace spaces with underscores
            std::replace(message.begin(), message.end(), ' ', '_');

            // Copy modified message back to buff
            strncpy(buff, message.c_str(), BUFF_MAXSIZE - 1);
            buff[BUFF_MAXSIZE - 1] = '\0'; // Ensure null-terminated string

            // Gửi lại chuỗi đã được xử lý cho client
            ret = send(NewConnection, buff, strlen(buff), 0);
            if (ret == SOCKET_ERROR)
            {
                cout << "Error with code " << WSAGetLastError() << endl;
                break;
            }
        }
    }
    shutdown(NewConnection, SD_BOTH);

    closesocket(NewConnection);
    closesocket(listenSock);
    WSACleanup();
    return 0;
}
