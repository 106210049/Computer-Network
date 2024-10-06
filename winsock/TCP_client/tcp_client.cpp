#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <string>
// g++ tcp_client.cpp -o tcp_client.exe -lws2_32
//  .\tcp_client.exe
#pragma comment(lib, "Ws2_32.lib")
#define SERVER_PORT 5500
#define SERVER_ADDR "127.0.0.1"

using namespace std;

int main()
{
    WSADATA wsaData;
    WORD wVersionRequested = MAKEWORD(2, 2);
    cout << "====== Set up Winsock ======" << endl;
    bool status = WSAStartup(wVersionRequested, &wsaData);
    if (status != 0)
    {
        cout << "Startup Winsock failed with error: " << WSAGetLastError() << endl;
        return 1;
    }
    cout << "WSAStartup completed." << endl;
    // Set up socket address structure
    sockaddr_in clientAddr;
    clientAddr.sin_family = AF_INET;
    clientAddr.sin_port = htons(SERVER_PORT);
    clientAddr.sin_addr.S_un.S_addr = inet_addr(SERVER_ADDR);
    // Create Socket
    SOCKET client = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

    if (client == INVALID_SOCKET)
    {
        cerr << "Creating socket failed with code " << WSAGetLastError() << endl;
        WSACleanup();
        return 1;
    }
    cout << "Creating socket completed successfully." << endl;
    if (connect(client, (sockaddr *)&clientAddr, sizeof(clientAddr)) == SOCKET_ERROR)
    {
        cout << "Connection failed with code " << WSAGetLastError() << endl;
        closesocket(client);
        WSACleanup();
        return 1;
    }
    cout << "Connection completed successfully." << endl;
    while (true)
    {
        string message;
        cout << "Enter message to send (type 'exit' to quit): ";
        getline(cin, message);
        int byteSent = send(client, message.c_str(), message.length(), 0);
        if (byteSent == SOCKET_ERROR)
        {
            cout << "Send failed with error: " << WSAGetLastError() << endl;
            closesocket(client);
            WSACleanup();
            return 1;
        }
        cout << "Message sent successfully." << endl;
        // Receive data from server
        char buffer[1024];
        int byteRecieved = recv(client, buffer, sizeof(buffer) - 1, 0);
        if (byteRecieved == SOCKET_ERROR)
        {
            cout << "Receive failed with error: " << WSAGetLastError() << endl;
        }
        else
        {
            buffer[byteRecieved] = '\0';
            cout << "Recieved from server: " << buffer << endl;
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
