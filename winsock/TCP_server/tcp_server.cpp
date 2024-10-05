#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <string>
#include <thread> // For multithreading
#include <vector>

#pragma comment(lib, "Ws2_32.lib")

#define SERVER_PORT 5500
#define SERVER_ADDR "127.0.0.1"
#define BUFF_MAXSIZE 1024

using namespace std;

// Function to handle each client in a separate thread
void handleClient(SOCKET clientSocket, sockaddr_in clientAddr)
{
    char buff[BUFF_MAXSIZE], clientIP[INET_ADDRSTRLEN];
    int ret, clientPort;

    // Convert client's IP address and port
    inet_ntop(AF_INET, &clientAddr.sin_addr, clientIP, sizeof(clientIP));
    clientPort = ntohs(clientAddr.sin_port);
    cout << "New connection established with client: " << clientIP << ":" << clientPort << endl;

    while (true)
    {
        // Receive data from client
        ret = recv(clientSocket, buff, BUFF_MAXSIZE, 0);
        if (ret == SOCKET_ERROR)
        {
            cout << "Error in receiving from client: " << WSAGetLastError() << endl;
            break;
        }
        if (ret == 0)
        {
            cout << "Client " << clientIP << ":" << clientPort << " disconnected." << endl;
            break;
        }

        buff[ret] = '\0'; // Null-terminate the received data
        cout << "Received from client " << clientIP << ":" << clientPort << ": " << buff << endl;

        // Check for 'exit' command from the client
        if (strcmp(buff, "exit") == 0)
        {
            cout << "Received exit command from client " << clientIP << ":" << clientPort << endl;
            const char *exitMessage = "exit";
            send(clientSocket, exitMessage, strlen(exitMessage), 0);
            break;
        }

        // Capitalize the first character if it's lowercase
        if (buff[0] >= 'a' && buff[0] <= 'z')
        {
            buff[0] = buff[0] - ('a' - 'A');
        }

        // Send modified data back to the client
        ret = send(clientSocket, buff, strlen(buff), 0);
        if (ret == SOCKET_ERROR)
        {
            cout << "Error in sending data to client: " << WSAGetLastError() << endl;
            break;
        }
    }

    // Shutdown and close client socket
    shutdown(clientSocket, SD_BOTH);
    closesocket(clientSocket);
    cout << "Connection with client " << clientIP << ":" << clientPort << " closed." << endl;
}

int main()
{
    cout << "====== Set up Winsock ======" << endl;
    WSADATA wsaData;
    WORD wVersion = MAKEWORD(2, 2);
    bool status = WSAStartup(wVersion, &wsaData);

    if (status != 0)
    {
        cout << "Startup winsock failed with error: " << WSAGetLastError() << endl;
        return 1;
    }
    cout << "Winsock initialized successfully." << endl;

    cout << "====== Set up socket ======" << endl;
    SOCKET listenSock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (listenSock == INVALID_SOCKET)
    {
        cout << "Creating socket failed with code " << WSAGetLastError() << endl;
        WSACleanup();
        return 1;
    }
    cout << "Socket created successfully." << endl;

    // Server address setup
    sockaddr_in tcpServerAddr;
    tcpServerAddr.sin_family = AF_INET;
    tcpServerAddr.sin_port = htons(SERVER_PORT);
    tcpServerAddr.sin_addr.s_addr = inet_addr(SERVER_ADDR);

    cout << "====== Bind API ======" << endl;
    if (bind(listenSock, (sockaddr *)&tcpServerAddr, sizeof(tcpServerAddr)) == SOCKET_ERROR)
    {
        cout << "Bind failed with error: " << WSAGetLastError() << endl;
        closesocket(listenSock);
        WSACleanup();
        return 1;
    }
    cout << "Bind completed successfully." << endl;

    cout << "====== Listen API ======" << endl;
    if (listen(listenSock, SOMAXCONN) == SOCKET_ERROR)
    {
        cout << "Listen failed with error: " << WSAGetLastError() << endl;
        closesocket(listenSock);
        WSACleanup();
        return 1;
    }
    cout << "Server is listening for connections..." << endl;

    vector<thread> clientThreads; // Vector to hold client threads

    while (true)
    {
        sockaddr_in clientAddr;
        int clientAddrLen = sizeof(clientAddr);
        SOCKET clientSock = accept(listenSock, (sockaddr *)&clientAddr, &clientAddrLen);
        if (clientSock == INVALID_SOCKET)
        {
            cout << "Accept failed with error: " << WSAGetLastError() << endl;
            closesocket(listenSock);
            WSACleanup();
            return 1;
        }

        // Start a new thread to handle the client
        clientThreads.push_back(thread(handleClient, clientSock, clientAddr));

        // Detach the thread to let it run independently
        clientThreads.back().detach();
    }

    // Clean up
    closesocket(listenSock);
    WSACleanup();
    return 0;
}
