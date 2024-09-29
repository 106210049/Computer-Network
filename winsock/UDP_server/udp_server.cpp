// cd UDP
// g++ udp_server.cpp -o udp_server.exe -lws2_32
// .\UDPServer.exe 8080

#include <bits/stdc++.h>
#include <winsock2.h> // Include the Windows Sockets API header
#include <stdio.h>
#include <ws2tcpip.h>
#include <iostream>
using namespace std;

string process(char *hostname)
{
    string st = "";
    struct addrinfo hints, *result, *rp;
    ZeroMemory(&hints, sizeof(hints));
    // hints.ai_family = AF_UNSPEC;     // Allow IPv4 or IPv6
    hints.ai_family = AF_INET;       // Allow IPv4
    hints.ai_socktype = SOCK_STREAM; // Use TCP

    int status = getaddrinfo(hostname, NULL, &hints, &result);
    if (status != 0)
    {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(status));
        WSACleanup();
        return "Not found information";
    }

    for (rp = result; rp != NULL; rp = rp->ai_next)
    {
        void *addr;
        char ipstr[INET6_ADDRSTRLEN];

        if (rp->ai_family == AF_INET)
        {
            struct sockaddr_in *ipv4 = (struct sockaddr_in *)rp->ai_addr;
            addr = &(ipv4->sin_addr);
        }
        else
        {
            struct sockaddr_in6 *ipv6 = (struct sockaddr_in6 *)rp->ai_addr;
            addr = &(ipv6->sin6_addr);
        }

        inet_ntop(rp->ai_family, addr, ipstr, sizeof(ipstr));
        string s(ipstr);
        st += "\n" + s;
    }

    freeaddrinfo(result);
    return st;
}

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        cerr << "Usage: serverUDP.exe <port_number>" << endl;
        return 1;
    }

    int port = atoi(argv[1]);
    cout << "argv[0]: " << argv[0] << endl;
    cout << "Port: " << port << endl;

    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
    {
        cerr << "WSAStartup failed!" << endl;
        return 1;
    }
    cout << "WSAStartup successfully!" << endl;

    SOCKET serverSocket = socket(AF_INET, SOCK_DGRAM, 0);
    if (serverSocket == INVALID_SOCKET)
    {
        cerr << "Socket creation failed!" << endl;
        WSACleanup();
        return 1;
    }
    cout << "Socket creates successfully!" << endl;

    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(port);

    if (bind(serverSocket, (sockaddr *)&serverAddr, sizeof(serverAddr)) ==
        SOCKET_ERROR)
    {
        cerr << "Binding failed!" << endl;
        closesocket(serverSocket);
        WSACleanup();
        return 1;
    }
    cout << "Binding successfully!" << endl;

    char buffer[1024];
    sockaddr_in clientAddr;
    int clientAddrLen = sizeof(clientAddr);

    while (true)
    {
        int bytesReceived = recvfrom(serverSocket, buffer, sizeof(buffer), 0,
                                     (sockaddr *)&clientAddr, &clientAddrLen);
        if (bytesReceived == SOCKET_ERROR)
        {
            cerr << "Error in recvfrom()" << endl;
            break;
        }

        buffer[bytesReceived] = '\0';

        string st = process(buffer);
        const char *message = st.c_str();

        sendto(serverSocket, message, strlen(message), 0, (sockaddr *)&clientAddr,
               clientAddrLen);
        }

    closesocket(serverSocket);
    WSACleanup();

    return 0;
}