# Precondition: Git for Windows 2.9.0 + Windows 7, other version of Git for Windows & Windows XP and Windows 10 should also be supported

# In /etc/ssh/sshd_config, set UsePrivilegeSeparation to no
# You can also change other settings of SSHD like port in this file

# Generate key pairs
ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -q -N ""
ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key -q -N ""
ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -q -N ""
ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -q -N ""

# Start SSHD
/usr/bin/sshd
