#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::Command;

fn start_brain() {
    let home = dirs::home_dir().unwrap_or_default();
    let brain_dir = home.join(".jarvis-orb");
    let brain_module = brain_dir.join("jarvis_brain");

    // Only start if brain is installed
    if !brain_module.exists() {
        eprintln!("[Orb] Brain not found at {:?}, running in standalone mode", brain_module);
        return;
    }

    let lib_dir = brain_dir.join("lib");
    let pythonpath = format!(
        "{}{}{}",
        lib_dir.display(),
        if cfg!(windows) { ";" } else { ":" },
        brain_dir.display()
    );

    // Find python
    let python = if cfg!(windows) { "python" } else { "python3" };

    match Command::new(python)
        .args(["-m", "jarvis_brain.demo_server"])
        .env("PYTHONPATH", &pythonpath)
        .current_dir(&brain_dir)
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .spawn()
    {
        Ok(child) => {
            eprintln!("[Orb] Brain started (PID: {})", child.id());
            // Don't wait — let it run as background process
            // It will be killed when Orb exits (child process)
            std::mem::forget(child);
        }
        Err(e) => {
            eprintln!("[Orb] Failed to start Brain: {}", e);
        }
    }
}

fn main() {
    // Start Brain Lite WebSocket server before Tauri
    start_brain();

    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running Jarvis Orb");
}
