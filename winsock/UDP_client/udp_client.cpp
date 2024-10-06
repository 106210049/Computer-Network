
//  g++ udp_client.cpp -o udp_client.exe -lws2_32
// ./udp_client.exe 127.0.0.1 8080 quora.com
// ./udp_client.exe 127.0.0.1 8080 www.google.com
// ./udp_client.exe 127.0.0.1 8080 sv.dut.udn.vn
// ./udp_client.exe 127.0.0.1 8080 www.youtube.com
// ./udp_client.exe 127.0.0.1 8080 lms.dut.udn.vn
#include <winsock2.h>
#include <ws2tcpip.h>
#include <bits/stdc++.h>

#pragma comment(lib, "ws2_32.lib")

using namespace std;

#define BUFFER_SIZE 1024

int main(int argc, char **argv)
{
    if (argc != 4)
    {
        cerr << "Execute the command: clientUDP.exe <server_IP> <port_number> <domain_name>" << endl;
        return 1;
    }

    const char *serverIP = argv[1];
    int portNumber = atoi(argv[2]);
    const char *domainName = argv[3];
    cout << "Server IP: " << argv[1] << " Port number: " << argv[2] << " domain number: " << argv[3] << endl;
    WSADATA wsaData;
    WORD wVersion = MAKEWORD(2, 2);
    if (WSAStartup(wVersion, &wsaData) != 0)
    {
        cout << "Initializing WinSock failed with code: " << WSAGetLastError() << endl;
        return 1;
    }
    else
    {
        cout << "Client startup complete!" << endl;
    }

    SOCKET clientSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (clientSocket == INVALID_SOCKET)
    {
        cout << "socket function failed with code: " << WSAGetLastError() << endl;
        WSACleanup();
        return 1;
    }

    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = inet_addr(serverIP);
    serverAddr.sin_port = htons(portNumber);

    int serverAddrLen = sizeof(serverAddr);
    char buffer[BUFFER_SIZE];
    int ret;

    while (true)
    {
        strcpy(buffer, domainName);

        ret = sendto(clientSocket, buffer, strlen(buffer), 0, (sockaddr *)&serverAddr, serverAddrLen);
        if (ret == SOCKET_ERROR)
        {
            cout << "Sending data failed with code: " << WSAGetLastError() << endl;
            break;
        }

        ret = recvfrom(clientSocket, buffer, BUFFER_SIZE, 0, (sockaddr *)&serverAddr, &serverAddrLen);
        if (ret == SOCKET_ERROR)
        {
            cout << "Received message from server : " << WSAGetLastError() << endl;
            break;
        }
        else if (ret == 0)
        {
            cout << "Server closed!" << endl;
            break;
        }
        else
        {
            buffer[ret] = '\0';
            cout << "Received IP address form server: " << buffer << endl;
            break;
        }
    }

    closesocket(clientSocket);
    WSACleanup();
    return 0;
}