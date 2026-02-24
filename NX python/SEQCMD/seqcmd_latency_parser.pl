#!/usr/bin/env perl

=head1 NAME

VODMA Command Latency Analyzer

=head1 DESCRIPTION

This script analyzes VODMA command latencies from ncverilog log files.

=head1 FEATURES

=over 4

=item * Tracks VODMA commands and their corresponding responses

=item * Calculates latency between command issue and completion

=item * Two analysis modes:
  - Separate mode: Analyze each VODMA type independently
  - Combined mode: Treat multiple VODMA types as a single client

=item * Provides detailed analysis including:
  - Command-by-command latency breakdown
  - Average latency across all commands
  - Maximum latency with detailed information
  - Total number of commands analyzed

=item * Time filtering: Analyze commands after specified timestamp (-t flag)

=back

=head1 USAGE

perl seqcmd_latency_parser.pl <logfile> [-c] [-t START_TIME] <vodma_type1> [vodma_type2 ...]

Options:
  -c : Combined mode - treat all VODMA types as single client
  -t START_TIME : Only analyze commands after this timestamp

Examples:
- Single type:     perl seqcmd_latency_parser.pl ncverilog.log vodma1yrr
- Separate types:  perl seqcmd_latency_parser.pl ncverilog.log vodma1yrr vodma1crr
- Combined types:  perl seqcmd_latency_parser.pl ncverilog.log -c vodma1yrr vodma1crr
- Time filter:     perl seqcmd_latency_parser.pl ncverilog.log -t 3000000 vodma1yrr

=cut

use strict;
use warnings;
use List::Util qw(sum max);
use Getopt::Long;
use Pod::Usage;

my $VERSION = '1.0';

# Main program
sub main {
    # Global variables
    my %vodma_commands; # tag -> [timestamp, vodma_type]
    my @latencies;      # [tag, vodma_type, start_time, end_time, latency]
    my @vodma_types;
    my %type_counts;    # Count of commands per type
    my $combined_mode = 0;
    my $start_time = 0;
    my $log_file;

    # Process command line arguments
    process_args(\$combined_mode, \$start_time, \$log_file, \@vodma_types);
    
    # Analyze the file
    analyze_file($log_file, $start_time, $combined_mode, \@vodma_types, \%vodma_commands, 
                 \@latencies, \%type_counts);
}

# Process command line arguments
sub process_args {
    my ($combined_mode_ref, $start_time_ref, $log_file_ref, $vodma_types_ref) = @_;
    my $help;
    
    GetOptions(
        "c" => $combined_mode_ref,
        "t=i" => $start_time_ref,
        "help|h" => \$help
    ) or pod2usage(1);
    
    pod2usage(-verbose => 2) if $help;
    
    # First argument should be log file
    $$log_file_ref = shift @ARGV;
    pod2usage("Error: No log file specified") unless defined $$log_file_ref;
    
    # Remaining arguments are vodma types
    @$vodma_types_ref = @ARGV;
    pod2usage("Error: No VODMA types specified") unless @$vodma_types_ref;
    
    # Print parsed arguments for verification
    print "\nParsed arguments:\n";
    print "Log file: $$log_file_ref\n";
    print "Start time: $$start_time_ref\n";
    print "VODMA types: ", join(", ", @$vodma_types_ref), "\n";
    print "Combined mode: ", $$combined_mode_ref ? "Yes" : "No", "\n\n";
}

# Parse a single line from the log file
sub parse_line {
    my ($line, $start_time, $vodma_types_ref, $vodma_commands_ref, 
        $latencies_ref, $type_counts_ref) = @_;
    
    # Extract timestamp at the start of the line
    my ($timestamp) = $line =~ /^(\d+)/;
    return unless defined $timestamp;
    
    # Skip if before start time
    return if $timestamp < $start_time;
    
    # Look for vodma commands
    foreach my $vodma_type (@$vodma_types_ref) {
        my ($tag) = $line =~ /\[seqcmd\].*\[\s*\Q$vodma_type\E\s*\].*tag\[(\d+)\]/;
        if (defined $tag) {
            $vodma_commands_ref->{$tag} = [$timestamp, $vodma_type];
            return;
        }
    }
    
    # Look for last data responses
    my ($tag) = $line =~ /\[data\].*tag\[(\d+)\].*last/;
    if (defined $tag && exists $vodma_commands_ref->{$tag}) {
        my ($cmd_start_time, $vodma_type) = @{$vodma_commands_ref->{$tag}};
        my $cmd_latency = $timestamp - $cmd_start_time;
        push @$latencies_ref, [$tag, $vodma_type, $cmd_start_time, $timestamp, $cmd_latency];
        $type_counts_ref->{$vodma_type}++;
        delete $vodma_commands_ref->{$tag};
    }
}

# Analyze the log file
sub analyze_file {
    my ($filename, $start_time, $combined_mode, $vodma_types_ref, 
        $vodma_commands_ref, $latencies_ref, $type_counts_ref) = @_;
    
    open(my $fh, '<', $filename) or die "Error: Cannot open file $filename: $!";
    
    while (my $line = <$fh>) {
        chomp $line;
        parse_line($line, $start_time, $vodma_types_ref, $vodma_commands_ref, 
                   $latencies_ref, $type_counts_ref);
    }
    
    close($fh);
    
    if ($combined_mode) {
        print_combined_analysis($start_time, $vodma_types_ref, $latencies_ref);
    } else {
        print_separate_analysis($start_time, $vodma_types_ref, $latencies_ref, $type_counts_ref);
    }
}

# Print analysis results in combined mode
sub print_combined_analysis {
    my ($start_time, $vodma_types_ref, $latencies_ref) = @_;
    
    if (@$latencies_ref == 0) {
        print "\nNo matching commands found with responses after timestamp $start_time.\n";
        return;
    }
    
    print "\nVodma Command Latency Analysis (Combined mode for: ", join(", ", @$vodma_types_ref), ")\n";
    print "Analysis starting from timestamp: $start_time\n";
    print "=" x 60, "\n";
    printf "%-10s %-12s %-12s %-8s\n", "Tag", "Start Time", "End Time", "Latency";
    print "-" x 60, "\n";
    
    # Sort latencies by start time and print
    foreach my $lat (sort { $a->[2] <=> $b->[2] } @$latencies_ref) {
        my ($tag, undef, $cmd_start, $cmd_end, $cmd_latency) = @$lat;
        printf "%-10s %-12s %-12s %-8s\n", $tag, $cmd_start, $cmd_end, $cmd_latency;
    }
    
    # Calculate stats
    my $total_latency = sum(map { $_->[4] } @$latencies_ref);
    my $avg_latency = $total_latency / scalar(@$latencies_ref);
    my $max_latency = max(map { $_->[4] } @$latencies_ref);
    my $max_lat_cmd;
    foreach my $lat (@$latencies_ref) {
        if ($lat->[4] == $max_latency) {
            $max_lat_cmd = $lat;
            last;
        }
    }
    
    print "\nSummary:\n";
    print "-" x 40, "\n";
    print "Total commands analyzed: ", scalar(@$latencies_ref), "\n";
    printf "Average latency: %.2f time units\n", $avg_latency;
    print "Maximum latency: $max_latency time units\n";
    
    print "\nMax latency command details:\n";
    print "  Tag: $max_lat_cmd->[0]\n";
    print "  Start time: $max_lat_cmd->[2]\n";
    print "  End time: $max_lat_cmd->[3]\n";
}

# Print analysis results in separate mode
sub print_separate_analysis {
    my ($start_time, $vodma_types_ref, $latencies_ref, $type_counts_ref) = @_;
    
    if (@$latencies_ref == 0) {
        print "\nNo matching commands found with responses after timestamp $start_time.\n";
        return;
    }
    
    print "\nVodma Command Latency Analysis for types: ", join(", ", @$vodma_types_ref), "\n";
    print "Analysis starting from timestamp: $start_time\n";
    print "=" x 80, "\n";
    printf "%-10s %-12s %-12s %-12s %-8s\n", "Tag", "Type", "Start Time", "End Time", "Latency";
    print "-" x 80, "\n";
    
    # Sort latencies by start time and print
    foreach my $lat (sort { $a->[2] <=> $b->[2] } @$latencies_ref) {
        my ($tag, $vtype, $cmd_start, $cmd_end, $cmd_latency) = @$lat;
        printf "%-10s %-12s %-12s %-12s %-8s\n", $tag, $vtype, $cmd_start, $cmd_end, $cmd_latency;
    }
    
    # Calculate overall stats
    my $total_latency = sum(map { $_->[4] } @$latencies_ref);
    my $avg_latency = $total_latency / scalar(@$latencies_ref);
    my $max_latency = max(map { $_->[4] } @$latencies_ref);
    my $max_lat_cmd;
    foreach my $lat (@$latencies_ref) {
        if ($lat->[4] == $max_latency) {
            $max_lat_cmd = $lat;
            last;
        }
    }
    
    print "\nSummary:\n";
    print "-" x 40, "\n";
    print "Total commands analyzed: ", scalar(@$latencies_ref), "\n";
    printf "Average latency: %.2f time units\n", $avg_latency;
    print "Maximum latency: $max_latency time units\n";
    
    print "\nBreakdown by type:\n";
    foreach my $vtype (sort keys %$type_counts_ref) {
        my @type_latencies = map { $_->[4] } grep { $_->[1] eq $vtype } @$latencies_ref;
        my $type_total = sum(@type_latencies);
        my $type_avg = $type_total / scalar(@type_latencies);
        print "  $vtype: $type_counts_ref->{$vtype} commands, avg latency: ";
        printf "%.2f\n", $type_avg;
    }
    
    print "\nMax latency command details:\n";
    print "  Tag: $max_lat_cmd->[0]\n";
    print "  Type: $max_lat_cmd->[1]\n";
    print "  Start time: $max_lat_cmd->[2]\n";
    print "  End time: $max_lat_cmd->[3]\n";
}

# Start execution
main();
