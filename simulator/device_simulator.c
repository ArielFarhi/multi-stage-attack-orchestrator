#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define DEFAULT_PORT 9000
#define BUFFER_SIZE 4096

static void send_response(int client_socket, const char *response)
{
    send(client_socket, response, strlen(response), 0);
}

static int handle_request(int client_socket, const char *request)
{
    if (strstr(request, "\"command\": \"get_info\"") != NULL ||
        strstr(request, "\"command\":\"get_info\"") != NULL)
    {
        send_response(
            client_socket,
            "{\"status\":\"ok\",\"model\":\"iPhone14\",\"ios\":\"17.2\",\"battery\":80}\n"
        );
        return 0;
    }

    if (strstr(request, "\"command\": \"run_stage\"") != NULL ||
        strstr(request, "\"command\":\"run_stage\"") != NULL)
    {
        if (strstr(request, "drop_connection") != NULL)
        {
            return 1;
        }

        if (strstr(request, "fail_stage") != NULL)
        {
            send_response(
                client_socket,
                "{\"status\":\"ok\",\"result\":\"failure\"}\n"
            );
            return 0;
        }

        send_response(
            client_socket,
            "{\"status\":\"ok\",\"result\":\"success\"}\n"
        );
        return 0;
    }

    if (strstr(request, "\"command\": \"list_files\"") != NULL ||
        strstr(request, "\"command\":\"list_files\"") != NULL)
    {
        send_response(
            client_socket,
            "{\"status\":\"ok\",\"files\":[\"/data/contacts.txt\",\"/data/notes.txt\"]}\n"
        );
        return 0;
    }

    if (strstr(request, "\"command\": \"read_file\"") != NULL ||
        strstr(request, "\"command\":\"read_file\"") != NULL)
    {
        if (strstr(request, "/data/contacts.txt") != NULL)
        {
            send_response(
                client_socket,
                "{\"status\":\"ok\",\"data\":\"Alice,123456\"}\n"
            );
            return 0;
        }

        if (strstr(request, "/data/notes.txt") != NULL)
        {
            send_response(
                client_socket,
                "{\"status\":\"ok\",\"data\":\"Example note\"}\n"
            );
            return 0;
        }

        send_response(
            client_socket,
            "{\"status\":\"error\",\"message\":\"File not found\"}\n"
        );
        return 0;
    }

    if (strstr(request, "\"command\": \"disconnect\"") != NULL ||
        strstr(request, "\"command\":\"disconnect\"") != NULL)
    {
        send_response(
            client_socket,
            "{\"status\":\"ok\"}\n"
        );
        return 1;
    }

    send_response(
        client_socket,
        "{\"status\":\"error\",\"message\":\"Unknown command\"}\n"
    );

    return 0;
}

int main(int argc, char *argv[])
{
    int server_socket;
    int client_socket;

    struct sockaddr_in server_address;
    struct sockaddr_in client_address;

    socklen_t client_length = sizeof(client_address);

    char buffer[BUFFER_SIZE];
    char request[BUFFER_SIZE];
    int port = DEFAULT_PORT;

    if (argc > 1)
    {
        port = atoi(argv[1]);

        if (port <= 0 || port > 65535)
        {
            fprintf(stderr, "Invalid port: %s\n", argv[1]);
            return 1;
        }
    }

    server_socket = socket(AF_INET, SOCK_STREAM, 0);

    if (server_socket < 0)
    {
        perror("socket");
        return 1;
    }

    int option = 1;

    setsockopt(
        server_socket,
        SOL_SOCKET,
        SO_REUSEADDR,
        &option,
        sizeof(option)
    );

    memset(&server_address, 0, sizeof(server_address));

    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = INADDR_ANY;
    server_address.sin_port = htons(port);

    if (bind(
            server_socket,
            (struct sockaddr *)&server_address,
            sizeof(server_address)
        ) < 0)
    {
        perror("bind");
        close(server_socket);
        return 1;
    }

    if (listen(server_socket, 5) < 0)
    {
        perror("listen");
        close(server_socket);
        return 1;
    }

    printf("Device simulator listening on port %d\n", port);
    fflush(stdout);

    while (1)
    {
        client_socket = accept(
            server_socket,
            (struct sockaddr *)&client_address,
            &client_length
        );

        if (client_socket < 0)
        {
            perror("accept");
            continue;
        }

        size_t request_length = 0;
        int disconnect_requested = 0;

        while (1)
        {
            int bytes_received = recv(
                client_socket,
                buffer,
                BUFFER_SIZE,
                0
            );

            if (bytes_received <= 0)
            {
                break;
            }

            for (int i = 0; i < bytes_received; i++)
            {
                if (buffer[i] == '\n')
                {
                    request[request_length] = '\0';
                    disconnect_requested = handle_request(
                        client_socket,
                        request
                    );
                    request_length = 0;

                    if (disconnect_requested)
                    {
                        break;
                    }
                }
                else if (request_length < BUFFER_SIZE - 1)
                {
                    request[request_length++] = buffer[i];
                }
                else
                {
                    send_response(
                        client_socket,
                        "{\"status\":\"error\",\"message\":\"Request too large\"}\n"
                    );
                    disconnect_requested = 1;
                    break;
                }
            }

            if (disconnect_requested)
            {
                break;
            }
        }

        close(client_socket);
    }

    close(server_socket);

    return 0;
}
