#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
// g++ udp_client.cpp -o udp_client.exe -lws2_32
// .\udp_client.exe
#pragma comment(lib, "Ws2_32.lib")

#define SERVER_ADDR "127.0.0.1"
#define SERVER_PORT 5500
#define BUFF_MAXSIZE 1024

using namespace std;

int main()
{
    // Khởi tạo Winsock
    cout << "====== Set up Winsock ======" << endl;
    WSADATA wsaData;
    WORD wVersion = MAKEWORD(2, 2);
    if (WSAStartup(wVersion, &wsaData) != 0)
    {
        cout << "Winsock initialization failed." << endl;
        return 1;
    }
    cout << "Winsock initialized successfully." << endl;

    // Tạo socket UDP
    cout << "====== Set up socket ======" << endl;
    SOCKET udpClientSock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpClientSock == INVALID_SOCKET)
    {
        cout << "Socket creation failed with error: " << WSAGetLastError() << endl;
        WSACleanup();
        return 1;
    }
    cout << "Socket setup successful." << endl;

    // Cấu hình địa chỉ server
    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_ADDR, &serverAddr.sin_addr);

    char message[BUFF_MAXSIZE];
    char buffer[BUFF_MAXSIZE];
    int serverAddrLen = sizeof(serverAddr);

    while (true)
    {
        cout << "Enter message to send (type 'exit' to quit): ";
        cin.getline(message, BUFF_MAXSIZE);

        // Gửi thông điệp tới server
        int ret = sendto(udpClientSock, message, strlen(message), 0, (sockaddr *)&serverAddr, serverAddrLen);
        if (ret == SOCKET_ERROR)
        {
            cout << "Error sending message: " << WSAGetLastError() << endl;
            break;
        }
        cout << "Message sent successfully." << endl;

        // Nhận thông điệp từ server
        int byteReceived = recvfrom(udpClientSock, buffer, BUFF_MAXSIZE - 1, 0, (sockaddr *)&serverAddr, &serverAddrLen);
        if (byteReceived == SOCKET_ERROR)
        {
            cout << "Receive failed with error: " << WSAGetLastError() << endl;
            break;
        }

        buffer[byteReceived] = '\0'; // Null-terminate the received message
        cout << "Received from server: " << buffer << endl;

        // Kiểm tra lệnh "exit"
        if (strcmp(buffer, "exit") == 0)
        {
            cout << "Server has closed the connection. Exiting..." << endl;
            break;
        }
    }

    // Đóng socket
    closesocket(udpClientSock);
    WSACleanup();
    return 0;
}
