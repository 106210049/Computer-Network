#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <string>
// g++ socket_tcp_client.cpp -o socket_tcp_client.exe -lws2_32
//  .\socket_tcp_client.exe
#pragma comment(lib, "Ws2_32.lib")

#define SERVER_PORT 5500
#define SERVER_ADDR "127.0.0.1"

using namespace std;

int main()
{
    WSADATA wsaData;
    WORD wVersionRequested = MAKEWORD(2, 2);

    cout << "====== Set up Winsock ======" << endl;

    // Initialize Winsock
    if (WSAStartup(wVersionRequested, &wsaData) != 0)
    {
        cerr << "Startup Winsock failed with error: " << WSAGetLastError() << endl;
        return 1;
    }
    cout << "WSAStartup completed." << endl;

    // Set up socket address structure
    sockaddr_in clientAddr;
    clientAddr.sin_family = AF_INET;                          // IPV4
    clientAddr.sin_port = htons(SERVER_PORT);                 // đổi port sang binary
    clientAddr.sin_addr.S_un.S_addr = inet_addr(SERVER_ADDR); // đổi địa chỉ sang binary

    // Create socket
    SOCKET client = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (client == INVALID_SOCKET)
    {
        cerr << "Creating socket failed with code " << WSAGetLastError() << endl;
        WSACleanup();
        return 1;
    }
    cout << "Creating socket completed successfully." << endl;

    // Connect to server
    if (connect(client, (sockaddr *)&clientAddr, sizeof(clientAddr)) == SOCKET_ERROR)
    {
        cerr << "Connection failed with code " << WSAGetLastError() << endl;
        closesocket(client);
        WSACleanup();
        return 1;
    }
    cout << "Connection completed successfully." << endl;
    while (1)
    {
        // Input message from user
        string message;

        cout << "Enter message to send: ";
        getline(cin, message);

        // Send message to server
        int bytesSent = send(client, message.c_str(), message.length(), 0);
        if (bytesSent == SOCKET_ERROR)
        {
            cerr << "Send failed with error: " << WSAGetLastError() << endl;
            closesocket(client);
            WSACleanup();
            return 1;
        }
        cout << "Message sent successfully." << endl;

        // Receive data from server
        char buffer[1024];
        int bytesReceived = recv(client, buffer, sizeof(buffer) - 1, 0);
        if (bytesReceived == SOCKET_ERROR)
        {
            cerr << "Receive failed with error: " << WSAGetLastError() << endl;
        }
        else
        {
            buffer[bytesReceived] = '\0'; // Null-terminate the received data
            cout << "Received from server: " << buffer << endl;
            if (strcmp(buffer, "exit") == 0)
            {
                cout << "Received exit command from server. Closing connection..." << endl;
                // const char *exitMessage = "exit.";
                // send(NewConnection, exitMessage, strlen(exitMessage), 0);
                break; // Exit the loop to close connection
            }
        }
    }
    // Shutdown and clean up
    shutdown(client, SD_BOTH);
    closesocket(client);
    WSACleanup();

    return 0;
}
