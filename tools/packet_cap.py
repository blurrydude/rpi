import pcapy
import argparse
import time
import sys
#43432451
def capture_packets(interface, port, promiscuous):
    # Open the network interface for packet capture
    capture = pcapy.open_live(interface, 65536, promiscuous, 0)

    # Set up the packet filter to capture packets on the specified port
    filter = 'tcp port {}'.format(port)
    capture.setfilter(filter)

    # Open a file to save the captured packets
    filename = 'captured_packets.txt'
    print(f'Starting packet capture on {interface}, port {port}...')
    start_time = time.time()
    i = 0
    while True:
        try:
            # Capture the next packet that matches the filter
            (header, packet) = capture.next()
            # Write the packet to the file
            with open(f"{filename}_{i}", 'w') as f:
                    f.write(str(packet) + '\n')
            i = i + 1
            elapsed_time = time.time() - start_time
            if elapsed_time > 120:  # Stop after 2 minutes
                print('Stopping packet capture...')
                sys.exit(0)
        except pcapy.PcapError:
            continue

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', required=True,
                        help='Name of the network interface to capture packets on')
    parser.add_argument('-p', '--port', type=int, required=True,
                        help='Port number to capture packets on')
    parser.add_argument('-a', '--all', action='store_true',
                        help='Enable promiscuous mode and capture all packets')
    args = parser.parse_args()

    # Capture packets on the specified port, with or without promiscuous mode
    promiscuous = args.all
    capture_packets(args.interface, args.port, promiscuous)
