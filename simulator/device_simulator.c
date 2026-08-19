#include <arpa/inet.h>
#include <ctype.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define DEFAULT_PORT 9000
#define BUFFER_SIZE 4096

typedef struct
{
    int unlocked;
    int stages_remaining;
} DeviceState;

static int is_command(const char *request, const char *expected)
{
    const char *field = strstr(request, "\"command\"");

    if (field == NULL)
    {
        return 0;
    }

    const char *value = strchr(field, ':');

    if (value == NULL)
    {
        return 0;
    }

    value++;
    while (isspace((unsigned char)*value))
    {
        value++;
    }

    size_t expected_length = strlen(expected);
    return *value == '"' &&
           strncmp(value + 1, expected, expected_length) == 0 &&
           value[expected_length + 1] == '"';
}

static int read_int_field(const char *request, const char *field_name, int *value)
{
    const char *field = strstr(request, field_name);

    if (field == NULL)
    {
        return 0;
    }

    const char *separator = strchr(field, ':');

    if (separator == NULL)
    {
        return 0;
    }

    *value = atoi(separator + 1);
    return 1;
}

static void send_response(int client_socket, const char *response)
{
    size_t total_sent = 0;
    size_t response_length = strlen(response);

    while (total_sent < response_length)
    {
        ssize_t sent = send(
            client_socket,
            response + total_sent,
            response_length - total_sent,
            0
        );

        if (sent <= 0)
        {
            return;
        }

        total_sent += (size_t)sent;
    }
}

static int handle_request(
    int client_socket,
    const char *request,
    DeviceState *state
)
{
    if (is_command(request, "get_info"))
    {
        send_response(
            client_socket,
            "{\"status\":\"ok\",\"model\":\"iPhone14\",\"ios\":\"17.2\",\"battery\":80}\n"
        );
        return 0;
    }

    if (is_command(request, "begin_attack"))
    {
        int stage_count;

        if (!read_int_field(request, "\"stage_count\"", &stage_count))
        {
            send_response(
                client_socket,
                "{\"status\":\"error\",\"message\":\"Missing stage_count\"}\n"
            );
            return 0;
        }

        if (stage_count <= 0)
        {
            send_response(
                client_socket,
                "{\"status\":\"error\",\"message\":\"Invalid stage_count\"}\n"
            );
            return 0;
        }

        state->unlocked = 0;
        state->stages_remaining = stage_count;
        send_response(client_socket, "{\"status\":\"ok\"}\n");
        return 0;
    }

    if (is_command(request, "run_stage"))
    {
        if (state->stages_remaining <= 0)
        {
            send_response(
                client_socket,
                "{\"status\":\"error\",\"message\":\"No active attack\"}\n"
            );
            return 0;
        }

        if (strstr(request, "drop_connection") != NULL)
        {
            return 1;
        }

        if (strstr(request, "fail_stage") != NULL)
        {
            state->stages_remaining = 0;
            state->unlocked = 0;
            send_response(
                client_socket,
                "{\"status\":\"ok\",\"result\":\"failure\"}\n"
            );
            return 0;
        }

        state->stages_remaining--;

        if (state->stages_remaining == 0)
        {
            state->unlocked = 1;
        }

        send_response(
            client_socket,
            "{\"status\":\"ok\",\"result\":\"success\"}\n"
        );
        return 0;
    }

    if (is_command(request, "list_files"))
    {
        if (!state->unlocked)
        {
            send_response(
                client_socket,
                "{\"status\":\"error\",\"message\":\"Access denied\"}\n"
            );
            return 0;
        }

        send_response(
            client_socket,
            "{\"status\":\"ok\",\"files\":[\"/data/contacts.txt\",\"/data/notes.txt\"]}\n"
        );
        return 0;
    }

    if (is_command(request, "read_file"))
    {
        if (!state->unlocked)
        {
            send_response(
                client_socket,
                "{\"status\":\"error\",\"message\":\"Access denied\"}\n"
            );
            return 0;
        }

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

    if (is_command(request, "disconnect"))
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

    signal(SIGPIPE, SIG_IGN);

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
        DeviceState state = {0};

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
                        request,
                        &state
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
