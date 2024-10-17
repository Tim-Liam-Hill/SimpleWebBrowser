#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

#define BUF_SIZE 500
/*
main.o google.com 80
*/
int main(int argc, char *argv[])
{
    int              s;
    char             buf[BUF_SIZE];
    size_t           len;
    ssize_t          nread;
    struct addrinfo  hints;
    struct addrinfo  *result, *rp;

    if (argc < 3) {
        fprintf(stderr, "Usage: %s host port msg...\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    /* Obtain address(es) matching host/port. */

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;    /* Allow IPv4 or IPv6 */
    hints.ai_socktype = SOCK_DGRAM; /* Datagram socket */
    hints.ai_flags = 0;
    hints.ai_protocol = 0;          /* Any protocol */

    s = getaddrinfo(argv[1], argv[2], &hints, &result);
    if (s != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(s));
        exit(EXIT_FAILURE);
    }

    /* getaddrinfo() returns a list of address structures.
        Try each address until we successfully connect(2).
        If socket(2) (or connect(2)) fails, we (close the socket
        and) try the next address. */

    for (rp = result; rp != NULL; rp = rp->ai_next) {
        //cast the sockaddr * to a sockaddr_in which gives access to the data we want
        struct sockaddr_in * sin = (struct sockaddr_in *) rp->ai_addr;
        char * ip = inet_ntoa(sin->sin_addr);
        printf("%s\n", ip);
    }
    //addrinfo contains ->
    /*
               struct addrinfo {
               int              ai_flags;
               int              ai_family;
               int              ai_socktype;
               int              ai_protocol;
               socklen_t        ai_addrlen;
               struct sockaddr *ai_addr; //WE WANT THIS
               char            *ai_canonname;
               struct addrinfo *ai_next;
           };

    */
    /*
           struct sockaddr {
           sa_family_t     sa_family;      
           char            sa_data[];     
       };
    */

    freeaddrinfo(result);           /* No longer needed */

    exit(EXIT_SUCCESS);
}