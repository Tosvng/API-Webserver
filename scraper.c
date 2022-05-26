// started with https://www.educative.io/edpresso/how-to-implement-tcp-sockets-in-c
// and the example in https://www.man7.org/linux/man-pages/man3/getaddrinfo.3.html

#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#include <netdb.h>  // For getaddrinfo
#include <unistd.h> // for close
#include <stdlib.h> // for exit

// char *input = argv[1];
int sockfd;
int out;
char address[100];
struct sockaddr_in server_addr;
char send_message[2000];
char receive_message[2000];
struct addrinfo hints;
struct addrinfo *result;
struct sockaddr_in *serverDetails;

int create_connection();
int main(int argc, char *argv[])
{
    char *raw = argv[1];
    char name[] = "";
    strcat(name, raw);
    printf("User name should be:%s\n", name);
    char memo[] = "";
    // printf("%s", argv);

    for (int i = 2; i < argc; i++)
    {
        char *word = argv[i];

        strcat(memo, word);
        strcat(memo, " ");
    }
    printf("memo is%s\n", memo);

    //****************************************POST REQUEST**************************************************
    create_connection();
    // POST memo from the user:
    /* header is:
    POST /api/memo HTTP/1.1
    Host: eagle.cs.umanitoba.ca:8547
    */

    char request[] = "POST /api/memo HTTP/1.1\r\nHost: eagle.cs.umanitoba.ca:8547\r\nCookie: id=";
    // strcat(request, "");
    strcat(request, name); // it doesn't concat properly
    strcat(request, "\r\n\r\nenterMemo=");
    strcat(request, memo);
    printf("Sending POST REQUEST:\n%s\n", request);
    // Send the message to server:
    printf("Sending request, %lu bytes\n", strlen(request));

    if (send(sockfd, request, strlen(request), 0) < 0)
    {
        printf("Unable to send message\n");
        return -1;
    }

    // Receive the server's response:
    if (recv(sockfd, receive_message, sizeof(receive_message), 0) < 0)
    {
        printf("Error while receiving server's msg\n");
        return -1;
    }
    printf("Server's response: %s\n", receive_message);

    // Close the socket:
    close(sockfd);

    //****************************************GET REQUEST**************************************************
    // GET memo from the user:
    /* header is:
    GET /api/memo HTTP/1.1
    Host: eagle.cs.umanitoba.ca:8547
    */

    create_connection();

    char newRequest[] = "GET /api/memo HTTP/1.1\r\nHost: eagle.cs.umanitoba.ca:8547\r\nCookie: id=";
    strcat(newRequest, name);

    printf("Sending GET REQUEST:\n%s\n", newRequest);
    // Send the message to server:
    printf("Sending request, %lu bytes\n", strlen(request));

    if (send(sockfd, newRequest, strlen(newRequest), 0) < 0)
    {
        printf("Unable to send message\n");
        return -1;
    }

    // Receive the server's response:
    if (recv(sockfd, receive_message, sizeof(receive_message), 0) < 0)
    {
        printf("Error while receiving server's msg\n");
        return -1;
    }

    printf("Server's response: %s\n", receive_message);
    // Close the socket:
    close(sockfd);

    //****************************************DELETE REQUEST**************************************************
    create_connection();
    // DELETE memo from the user:
    /* header is:
    DELETE /api/memo/<id> HTTP/1.1
    Host: eagle.cs.umanitoba.ca:8547
    */

    char delteteRequest[] = "DELETE /api/memo/id=TOM";
    strcat(delteteRequest, name);
    strcat(delteteRequest, "&0 HTTP/1.1\r\nHost: eagle.cs.umanitoba.ca:8547\r\nCookie: id=");
    strcat(delteteRequest, name);
    strcat(delteteRequest, "\r\n\r\n");

    printf("Sending DELETE REQUEST:\n%s\n", request);
    // Send the message to server:
    printf("Sending delteteRequest, %lu bytes\n", strlen(delteteRequest));

    if (send(sockfd, delteteRequest, strlen(delteteRequest), 0) < 0)
    {
        printf("Unable to send message\n");
        return -1;
    }

    // Receive the server's response:
    if (recv(sockfd, receive_message, sizeof(receive_message), 0) < 0)
    {
        printf("Error while receiving server's msg\n");
        return -1;
    }
    printf("Server's response: %s\n", receive_message);

    // Close the socket:
    close(sockfd);

    //****************************************GET REQUEST**************************************************
    create_connection();
    // GET memo from the user:
    /* header is:
    GET /api/memo HTTP/1.1
    Host: eagle.cs.umanitoba.ca:8547
    */

    char newGETRequest[] = "GET /api/memo HTTP/1.1\r\nHost: eagle.cs.umanitoba.ca:8547\r\nCookie: id=";
    strcat(newGETRequest, name);
    printf("Sending another GET REQUEST:\n%s\n", newGETRequest);
    // Send the message to server:
    printf("Sending new GET request, %lu bytes\n", strlen(newGETRequest));
    printf("");

    if (send(sockfd, newGETRequest, strlen(newGETRequest), 0) < 0)
    {
        printf("Unable to send message\n");
        return -1;
    }

    // Receive the server's response:
    if (recv(sockfd, receive_message, sizeof(receive_message), 0) < 0)
    {
        printf("Error while receiving server's msg\n");
        return -1;
    }

    printf("Server's response: %s\n", receive_message);
    // Close the socket:
    close(sockfd);

    //****************************************PUT REQUEST**************************************************
    create_connection();
    // PUT memo from the user:
    /* header is:
    PUT /api/memo HTTP/1.1
    Host: eagle.cs.umanitoba.ca:8547
    */

    char PUTrequest[] = "PUT /api/memo/id=";
    strcat(PUTrequest, name);
    strcat(PUTrequest, "&0 HTTP/1.1\r\nHost: eagle.cs.umanitoba.ca:8547\r\nCookie: id=");
    strcat(PUTrequest, name);
    strcat(PUTrequest, "\r\n\r\nenterMemo=updating..");
    printf("Sending PUT REQUEST:\n%s\n", PUTrequest);
    // Send the message to server:
    printf("Sending request, %lu bytes\n", strlen(PUTrequest));

    if (send(sockfd, PUTrequest, strlen(PUTrequest), 0) < 0)
    {
        printf("Unable to send message\n");
        return -1;
    }

    // Receive the server's response:
    if (recv(sockfd, receive_message, sizeof(receive_message), 0) < 0)
    {
        printf("Error while receiving server's msg\n");
        return -1;
    }
    printf("Server's response: %s\n", receive_message);

    // Close the socket:
    close(sockfd);
}

int create_connection()
{
    // Clean buffers:
    memset(send_message, '\0', sizeof(send_message));
    memset(receive_message, '\0', sizeof(receive_message));

    // create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        printf("Unable to create socket\n");
        return -1;
    }

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = PF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags |= AI_CANONNAME;

    // get the ip of the page we want to scrape
    out = getaddrinfo("eagle.cs.umanitoba.ca", NULL, &hints, &result);
    // fail gracefully
    if (out != 0)
    {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(out));
        exit(EXIT_FAILURE);
    }

    // ai_addr is a struct sockaddr
    // so, we can just use that sin_addr
    serverDetails = (struct sockaddr_in *)result->ai_addr;

    // Set port and IP the same as server-side:
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8547);
    // server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    server_addr.sin_addr = serverDetails->sin_addr;

    // converts to octets
    printf("Convert...\n");
    inet_ntop(server_addr.sin_family, &server_addr.sin_addr, address, 100);
    printf("Connecting to %s\n", address);

    // Send connection request to server:
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        printf("Unable to connect\n");
        exit(EXIT_FAILURE);
    }
    printf("Connected with server successfully\n");
    return 0;
}