import dns.resolver

RESOLVERS = ['8.8.8.8', '1.1.1.1', '8.67.222.222', '45.90.28.190', '103.86.96.100', '8.26.56.26', '185.228.168.9', '208.67.222.222', '208.67.222.222']

def lookup(domain_full):
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = RESOLVERS
    try:
        answers = resolver.resolve(domain_full, 'A')
        ips = [rdata.address for rdata in answers]
        return 'taken', ips
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return 'available', []
    except Exception as e:
        return 'error', [str(e)]
