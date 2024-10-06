#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <thread>
#include <vector>
// g++ udp_server.cpp -o udp_server.exe -lws2_32
// .\udp_server.exe
#pragma comment(lib, "Ws2_32.lib")

#define SERVER_PORT 5500
#define BUFF_MAXSIZE 1024

using namespace std;

int main()
{
    // Initialize Winsock
    cout << "====== Set up Winsock ======" << endl;
    WSADATA wsaData;
    WORD wVersion = MAKEWORD(2, 2);
    if (WSAStartup(wVersion, &wsaData) != 0)
    {
        cout << "Winsock initialization failed." << endl;
        return 1;
    }
    cout << "Winsock initialized successfully." << endl;
    // Create UDP socket
    cout << "====== Set up socket ======" << endl;
    SOCKET udpServerSock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udpServerSock == INVALID_SOCKET)
    {
        cout << "Socket creation failed with error: " << WSAGetLastError() << endl;
        WSACleanup();
        return 1;
    }
    cout << "Set up socket susscessfull" << endl;
    // Server address setup
    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(SERVER_PORT);
    serverAddr.sin_addr.s_addr = INADDR_ANY;

    // Bind socket to the server address
    cout << "====== Bind API ======" << endl;
    if (bind(udpServerSock, (sockaddr *)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR)
    {
        cout << "Bind failed with error: " << WSAGetLastError() << endl;
        closesocket(udpServerSock);
        WSACleanup();
        return 1;
    }
    cout << "Bind API susscessfull" << endl;
    cout << "UDP server is ready to receive messages..." << endl;

    sockaddr_in clientAddr;
    int clientAddrLen = sizeof(clientAddr);
    char buffer[BUFF_MAXSIZE];

    while (true)
    {
        // Receive message from client
        int ret = recvfrom(udpServerSock, buffer, BUFF_MAXSIZE, 0, (sockaddr *)&clientAddr, &clientAddrLen);
        if (ret == SOCKET_ERROR)
        {
            cout << "Error receiving message: " << WSAGetLastError() << endl;
            break;
        }

        buffer[ret] = '\0'; // Null-terminate the received message
        cout << "Received message from client: " << buffer << endl;

        // Check for "exit" command
        if (strcmp(buffer, "exit") == 0)
        {
            cout << "Exit command received. Server is shutting down." << endl;
            const char *exitMessage = "exit";
            sendto(udpServerSock, exitMessage, strlen(exitMessage), 0, (sockaddr *)&clientAddr, clientAddrLen);
            break;
        }

        ret = sendto(udpServerSock, buffer, strlen(buffer), 0, (sockaddr *)&clientAddr, clientAddrLen);
        if (ret == SOCKET_ERROR)
        {
            cout << "Error in sending data to client: " << WSAGetLastError() << endl;
            break;
        }
    }

    // Close socket
    closesocket(udpServerSock);
    WSACleanup();
    return 0;
}
