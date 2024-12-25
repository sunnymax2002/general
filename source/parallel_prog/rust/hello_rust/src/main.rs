use std::thread;
use std::time::Duration;

fn main() {
    /* Spawning threads
    thread::spawn(|| {
        for i in 1..100 {
            println!("hi number {} from the spawned thread!", i);
            thread::sleep(Duration::from_millis(1));
        }
    });

    for i in 1..50 {
        println!("hi number {} from the main thread!", i);
        thread::sleep(Duration::from_millis(1));
    } */

    /* References: To see if rust compiler introduces barrier before creating mutable reference to prevent HW re-ordering the statements
     */
    let mut s = String::from("hello");

    let r1 = &s; // no problem
    let r2 = &s; // no problem
    println!("{} and {}", r1, r2);
    // variables r1 and r2 will not be used after this point

    let r3 = &mut s; // no problem
    println!("{}", r3);
}