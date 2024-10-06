// g++ udp_server.cpp -o udp_server.exe -lws2_32
// .\udp_server.exe 8080

#include <winsock2.h>
#include <ws2tcpip.h>
#include <bits/stdc++.h>

#pragma comment(lib, "ws2_32.lib")

using namespace std;

#define SERVER_ADDR "127.0.0.1"
#define BUFFER_SIZE 1024

string process(const string &input)
{
    addrinfo *result;
    int addressInfo;
    addrinfo hints = {0};
    hints.ai_family = AF_INET;

    addressInfo = getaddrinfo(input.c_str(), NULL, &hints, &result);
    if (addressInfo != 0)
    {
        return "Not found!";
    }
    else
    {

        sockaddr_in *addrress = (sockaddr_in *)result->ai_addr;
        char ip[INET_ADDRSTRLEN];

        inet_ntop(AF_INET, &(addrress->sin_addr), ip, INET_ADDRSTRLEN);
        freeaddrinfo(result);
        return string(ip);
    }
}

int main(int argc, char **argv)
{
    if (argc != 2)
    {
        cout << "Execute the command: serverUDP.exe <port_number>" << endl;
        return 1;
    }

    int portNumber = atoi(argv[1]);

    WSADATA wsaData;
    WORD wVersion = MAKEWORD(2, 2);
    if (WSAStartup(wVersion, &wsaData) != 0)
    {
        cout << "Initializing WinSock failed with code: " << WSAGetLastError() << endl;
        return 1;
    }
    else
    {
        cout << "Server startup complete!" << endl;
    }
    cout << "========== Create Socket ==========" << endl;
    SOCKET serverSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (serverSocket == INVALID_SOCKET)
    {
        cout << "Creating socket failed with code: " << WSAGetLastError() << endl;
        WSACleanup();
        return 1;
    }
    cout << "Create socket susscessful" << endl;
    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = inet_addr(SERVER_ADDR);
    serverAddr.sin_port = htons(portNumber);
    cout << "========== BIND API ==========" << endl;
    if (bind(serverSocket, (sockaddr *)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR)
    {
        cout << "Binding socket failed with code: " << WSAGetLastError() << endl;
        closesocket(serverSocket);
        WSACleanup();
        return 1;
    }

    sockaddr_in clientAddr;
    int clientAddrLen = sizeof(clientAddr);
    char buffer[BUFFER_SIZE];
    int ret;
    cout << "========== Recieve data ==========" << endl;
    while (true)
    {
        ret = recvfrom(serverSocket, buffer, BUFFER_SIZE, 0, (sockaddr *)&clientAddr, &clientAddrLen);
        if (ret == SOCKET_ERROR)
        {
            cout << "Receiving data failed with code: " << WSAGetLastError() << endl;
            continue;
        }
        else if (ret == 0)
        {
            cout << "Client disconnected!" << endl;
            continue;
        }
        else
        {
            buffer[ret] = '\0';
            cout << "Received domain name from client : " << buffer << endl;
        }

        string message(buffer);
        message = process(message);
        strcpy(buffer, message.c_str());

        if (sendto(serverSocket, buffer, strlen(buffer), 0, (sockaddr *)&clientAddr, clientAddrLen) == SOCKET_ERROR)
        {
            cout << "Sending data failed with code: " << WSAGetLastError() << endl;
            continue;
        }
        cout << "IP address: " << buffer << endl;
    }

    closesocket(serverSocket);
    WSACleanup();
    return 0;
}