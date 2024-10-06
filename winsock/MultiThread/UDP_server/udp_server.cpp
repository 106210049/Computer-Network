#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
// g++ udp_server.cpp -o udp_server.exe -lws2_32
// .\udp_server.exe
#pragma comment(lib, "Ws2_32.lib")

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
    SOCKET udpServerSock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpServerSock == INVALID_SOCKET)
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
    serverAddr.sin_addr.s_addr = INADDR_ANY;

    // Liên kết socket với địa chỉ server
    cout << "====== Bind API ======" << endl;
    if (bind(udpServerSock, (sockaddr *)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR)
    {
        cout << "Bind failed with error: " << WSAGetLastError() << endl;
        closesocket(udpServerSock);
        WSACleanup();
        return 1;
    }
    cout << "Bind API successful." << endl;
    cout << "UDP server is ready to receive messages..." << endl;

    // Biến để lưu thông điệp từ client
    char buffer[BUFF_MAXSIZE];
    sockaddr_in clientAddr;
    int clientAddrLen = sizeof(clientAddr);

    while (true)
    {
        // Đợi thông điệp từ client
        int ret = recvfrom(udpServerSock, buffer, BUFF_MAXSIZE, 0, (sockaddr *)&clientAddr, &clientAddrLen);
        if (ret == SOCKET_ERROR)
        {
            cout << "Error receiving message: " << WSAGetLastError() << endl;
            break;
        }

        buffer[ret] = '\0'; // Null-terminate the received message

        char clientIP[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &clientAddr.sin_addr, clientIP, sizeof(clientIP));
        int clientPort = ntohs(clientAddr.sin_port);

        cout << "Received message from client " << clientIP << ":" << clientPort << " : " << buffer << endl;

        // Kiểm tra lệnh "exit"
        if (strcmp(buffer, "exit") == 0)
        {
            cout << "Exit command received from client. Closing connection." << endl;
            const char *exitMessage = "exit";
            sendto(udpServerSock, exitMessage, strlen(exitMessage), 0, (sockaddr *)&clientAddr, clientAddrLen);
            break;
        }

        // Gửi lại thông điệp cho client
        ret = sendto(udpServerSock, buffer, strlen(buffer), 0, (sockaddr *)&clientAddr, clientAddrLen);
        if (ret == SOCKET_ERROR)
        {
            cout << "Error in sending data to client: " << WSAGetLastError() << endl;
            break;
        }
    }

    // Đóng socket
    closesocket(udpServerSock);
    WSACleanup();
    return 0;
}
