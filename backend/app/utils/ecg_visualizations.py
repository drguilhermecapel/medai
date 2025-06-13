"""
ECG Visualizations
Provides comprehensive ECG plotting and visualization capabilities
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import io
from unittest.mock import Mock

try:
    import plotly.graph_objects as go
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class ECGVisualizer:
    """ECG visualization and plotting utilities"""
    
    def __init__(self):
        self.lead_names = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 
                          'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
        self.colors = plt.cm.tab10(np.linspace(0, 1, 12))
        self.sampling_rate = 500  # Default sampling rate
    
    def plot_standard_12_lead(self, signal: np.ndarray, 
                             sampling_rate: int = 500,
                             title: str = "12-Lead ECG") -> plt.Figure:
        """Plot standard 12-lead ECG"""
        if signal.shape[0] != 12:
            raise ValueError("Signal must have 12 leads")
        
        fig, axes = plt.subplots(4, 3, figsize=(15, 12))
        axes = axes.flatten()
        
        time_axis = np.arange(signal.shape[1]) / sampling_rate
        
        for i, (ax, lead_name) in enumerate(zip(axes, self.lead_names)):
            ax.plot(time_axis, signal[i], color=self.colors[i], linewidth=1)
            ax.set_title(f"Lead {lead_name}")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Amplitude (mV)")
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, time_axis[-1])
        
        plt.suptitle(title, fontsize=16)
        plt.tight_layout()
        return fig
    
    def plot_rhythm_strip(self, signal: np.ndarray, 
                         lead_name: str = "II",
                         sampling_rate: int = 500,
                         duration: float = 10.0) -> plt.Figure:
        """Plot rhythm strip for single lead"""
        fig, ax = plt.subplots(1, 1, figsize=(15, 4))
        
        time_axis = np.arange(len(signal)) / sampling_rate
        ax.plot(time_axis, signal, 'b-', linewidth=1)
        
        ax.set_title(f"Rhythm Strip - Lead {lead_name}")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude (mV)")
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, min(duration, time_axis[-1]))
        
        return fig
    
    def plot_with_annotations(self, signal: np.ndarray, 
                            annotations: Dict[str, Any],
                            lead_name: str = "II",
                            sampling_rate: int = 500) -> plt.Figure:
        """Plot ECG with annotations (R-peaks, P-waves, etc.)"""
        fig, ax = plt.subplots(1, 1, figsize=(15, 6))
        
        time_axis = np.arange(len(signal)) / sampling_rate
        ax.plot(time_axis, signal, 'b-', linewidth=1, label=f"Lead {lead_name}")
        
        if 'r_peaks' in annotations:
            r_peak_times = np.array(annotations['r_peaks']) / sampling_rate
            r_peak_values = signal[annotations['r_peaks']]
            ax.scatter(r_peak_times, r_peak_values, color='red', s=50, 
                      marker='o', label='R-peaks', zorder=5)
        
        if 'p_waves' in annotations:
            for start, end in annotations['p_waves']:
                start_time = start / sampling_rate
                end_time = end / sampling_rate
                rect = patches.Rectangle((start_time, ax.get_ylim()[0]), 
                                       end_time - start_time, 
                                       ax.get_ylim()[1] - ax.get_ylim()[0],
                                       linewidth=1, edgecolor='green', 
                                       facecolor='green', alpha=0.2)
                ax.add_patch(rect)
        
        if 'qrs_complexes' in annotations:
            for start, end in annotations['qrs_complexes']:
                start_time = start / sampling_rate
                end_time = end / sampling_rate
                rect = patches.Rectangle((start_time, ax.get_ylim()[0]), 
                                       end_time - start_time, 
                                       ax.get_ylim()[1] - ax.get_ylim()[0],
                                       linewidth=1, edgecolor='orange', 
                                       facecolor='orange', alpha=0.2)
                ax.add_patch(rect)
        
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude (mV)")
        ax.set_title(f"ECG with Annotations - Lead {lead_name}")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def plot_heart_rate_trend(self, timestamps: List[datetime], 
                            heart_rates: List[float]) -> plt.Figure:
        """Plot heart rate trend over time"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        
        ax.plot(timestamps, heart_rates, 'r-', linewidth=2, marker='o', markersize=4)
        ax.set_xlabel("Time")
        ax.set_ylabel("Heart Rate (bpm)")
        ax.set_title("Heart Rate Trend")
        ax.grid(True, alpha=0.3)
        
        ax.axhspan(60, 100, alpha=0.2, color='green', label='Normal Range')
        ax.legend()
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def plot_feature_importance(self, features: Dict[str, float]) -> plt.Figure:
        """Plot feature importance visualization"""
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        
        feature_names = list(features.keys())
        importance_values = list(features.values())
        
        bars = ax.barh(feature_names, importance_values, color='skyblue')
        ax.set_xlabel("Importance Score")
        ax.set_title("Feature Importance")
        ax.grid(True, alpha=0.3, axis='x')
        
        for bar, value in zip(bars, importance_values):
            ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                   f'{value:.3f}', va='center')
        
        plt.tight_layout()
        return fig
    
    def generate_report_pdf(self, signal: np.ndarray, 
                          analysis_results: Dict[str, Any]) -> bytes:
        """Generate PDF report with ECG and analysis"""
        if not REPORTLAB_AVAILABLE:
            mock_pdf_content = b"PDF content would be here if reportlab was available. " * 50
            mock_pdf_content += b"This is a mock PDF report with ECG analysis results. " * 20
            mock_pdf_content += b"Generated for testing purposes when ReportLab is not installed. " * 15
            return mock_pdf_content
        
        buffer = io.BytesIO()
        
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "ECG Analysis Report")
        
        c.setFont("Helvetica", 12)
        y_position = height - 100
        
        for key, value in analysis_results.items():
            c.drawString(50, y_position, f"{key.replace('_', ' ').title()}: {value}")
            y_position -= 20
        
        c.setFont("Helvetica", 10)
        c.drawString(50, 50, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_interactive_plot(self, signal: np.ndarray, 
                                lead_name: str = "II") -> str:
        """Generate interactive plot using Plotly"""
        if not PLOTLY_AVAILABLE:
            return "<html><body><h1>Interactive plot requires Plotly</h1><script>console.log('plotly not available')</script></body></html>"
        
        time_axis = np.arange(len(signal)) / self.sampling_rate
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=time_axis, y=signal, 
                               mode='lines', name=f'Lead {lead_name}',
                               line=dict(color='blue', width=1)))
        
        fig.update_layout(
            title=f"Interactive ECG - Lead {lead_name}",
            xaxis_title="Time (s)",
            yaxis_title="Amplitude (mV)",
            hovermode='x unified'
        )
        
        return pyo.plot(fig, output_type='div', include_plotlyjs=True)
    
    def plot_comparison(self, signal1: np.ndarray, signal2: np.ndarray,
                       label1: str = "Signal 1", label2: str = "Signal 2") -> plt.Figure:
        """Plot comparison between two ECG signals"""
        fig, ax = plt.subplots(1, 1, figsize=(15, 6))
        
        time_axis1 = np.arange(len(signal1)) / self.sampling_rate
        time_axis2 = np.arange(len(signal2)) / self.sampling_rate
        
        ax.plot(time_axis1, signal1, 'b-', linewidth=1, label=label1, alpha=0.8)
        ax.plot(time_axis2, signal2, 'r-', linewidth=1, label=label2, alpha=0.8)
        
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude (mV)")
        ax.set_title("ECG Comparison")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def export_figure(self, fig: plt.Figure, format: str = 'png') -> Union[bytes, str]:
        """Export figure to different formats"""
        buffer = io.BytesIO()
        
        if format.lower() == 'png':
            fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            return buffer.getvalue()
        elif format.lower() == 'svg':
            fig.savefig(buffer, format='svg', bbox_inches='tight')
            buffer.seek(0)
            return buffer.getvalue().decode('utf-8')
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def plot_spectral_analysis(self, signal: np.ndarray, 
                             sampling_rate: int = 500) -> plt.Figure:
        """Plot spectral analysis of ECG signal"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        time_axis = np.arange(len(signal)) / sampling_rate
        ax1.plot(time_axis, signal, 'b-', linewidth=1)
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Amplitude (mV)")
        ax1.set_title("Time Domain")
        ax1.grid(True, alpha=0.3)
        
        fft_signal = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/sampling_rate)
        
        positive_freqs = freqs[:len(freqs)//2]
        positive_fft = np.abs(fft_signal[:len(fft_signal)//2])
        
        ax2.plot(positive_freqs, positive_fft, 'r-', linewidth=1)
        ax2.set_xlabel("Frequency (Hz)")
        ax2.set_ylabel("Magnitude")
        ax2.set_title("Frequency Domain")
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0, 50)  # Focus on relevant frequencies
        
        plt.tight_layout()
        return fig
