use std::fs::File;
use std::io::{self, Write};
use std::time::Duration;
use csv::ReaderBuilder;
use clap::{Parser, ValueEnum};

#[derive(Parser)]
struct Cli {
    /// The COM port to use (e.g., COM1)
    #[clap(short, long, default_value = "COM1")]
    com_port: String,

    /// The baud rate for transmission
    #[clap(short, long, default_value_t = 9600)]
    baud_rate: u32,

    /// Mode of operation: transmit or receive
    #[clap(short, long, value_parser)]
    mode: Mode,

    /// Path to the telemetry data CSV file (used only in file-based transmit mode)
    #[clap(short, long)]
    file_path: Option<String>,

    /// Data to directly send (used only in direct send mode)
    #[clap(long, conflicts_with = "file_path")]
    send: Option<String>,

    /// Enable loop mode to continuously retransmit the CSV file
    #[clap(long)]
    loop_mode: bool,

    /// Custom delimiter for transmission (default is "\n")
    #[clap(long, default_value = "\n")]
    delimiter: String,
}

#[derive(Copy, Clone, PartialEq, Eq, ValueEnum)]
enum Mode {
    Transmit,
    Receive,
}

fn main() -> io::Result<()> {
    // Parse command line arguments
    let args = Cli::parse();

    // Set up the serial port
    let port_name = &args.com_port;
    let baud_rate = args.baud_rate;
    let mut port = serialport::new(port_name, baud_rate)
        .timeout(Duration::from_millis(10))
        .open()
        .expect("Failed to open serial port");

    match args.mode {
        Mode::Transmit => {
            // Check if `send` option is provided
            if let Some(data) = args.send {
                // Directly send the specified data
                loop {
                    port.write_all(data.as_bytes())?;
                    port.write_all(args.delimiter.as_bytes())?; // Send custom delimiter
                    println!("Sent: {}", data);

                    // Exit loop if loop_mode is not enabled
                    if !args.loop_mode {
                        break;
                    }

                    // Add a delay to simulate transmission interval
                    std::thread::sleep(Duration::from_secs(1));
                }
            } else if let Some(file_path) = args.file_path {
                // Open the CSV file for reading and send each record
                loop {
                    let file = File::open(&file_path).expect("Failed to open telemetry data CSV file");
                    let mut csv_reader = ReaderBuilder::new()
                        .has_headers(true)
                        .from_reader(file);

                    for result in csv_reader.records() {
                        let record = result.expect("Failed to read CSV record");
                        let telemetry_data: String = record.iter().map(|field| field.to_string()).collect::<Vec<_>>().join(",");

                        port.write_all(telemetry_data.as_bytes())?;
                        port.write_all(args.delimiter.as_bytes())?;
                        println!("Sent: {}", telemetry_data);

                        std::thread::sleep(Duration::from_secs(1));
                    }

                    if !args.loop_mode {
                        break;
                    }
                }
            } else {
                eprintln!("Error: Either --file_path or --send must be provided in transmit mode.");
            }
        }
        Mode::Receive => {
            let mut serial_buf: Vec<u8> = vec![0; 1000];
            println!("Receiving data on {} at {} baud:", port_name, baud_rate);

            loop {
                match port.read(serial_buf.as_mut_slice()) {
                    Ok(t) => {
                        io::stdout().write_all(&serial_buf[..t]).unwrap();
                        io::stdout().flush().unwrap();
                    }
                    Err(ref e) if e.kind() == io::ErrorKind::TimedOut => (),
                    Err(e) => eprintln!("{:?}", e),
                }
            }
        }
    }

    Ok(())
}
