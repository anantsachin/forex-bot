import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, CandlestickSeries, LineSeries } from 'lightweight-charts';

const Chart = ({ data, prediction, tradeLevels, predictedCandle, futurePath, council }) => {
    const chartContainerRef = useRef();
    const chartRef = useRef();

    useEffect(() => {
        if (!chartContainerRef.current) return;

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: 'transparent' },
                textColor: '#9CA3AF',
            },
            grid: {
                vertLines: { color: '#374151' },
                horzLines: { color: '#374151' },
            },
            width: chartContainerRef.current.clientWidth,
            height: chartContainerRef.current.clientHeight,
            timeScale: {
                borderColor: '#4B5563',
            },
            rightPriceScale: {
                borderColor: '#4B5563',
            },
        });

        const candlestickSeries = chart.addSeries(CandlestickSeries, {
            upColor: '#10B981',
            downColor: '#EF4444',
            borderVisible: true,
            borderUpColor: '#10B981',
            borderDownColor: '#EF4444',
            wickUpColor: '#10B981',
            wickDownColor: '#EF4444',
        });

        if (data && data.length > 0) {
            candlestickSeries.setData(data);

            // Add Future Path (Ghost Candles)
            if (futurePath && futurePath.length > 0) {
                const futureSeries = chart.addSeries(CandlestickSeries, {
                    upColor: 'rgba(16, 185, 129, 0.2)',
                    downColor: 'rgba(239, 68, 68, 0.2)',
                    borderVisible: true,
                    borderUpColor: 'rgba(16, 185, 129, 0.5)',
                    borderDownColor: 'rgba(239, 68, 68, 0.5)',
                    wickUpColor: 'rgba(16, 185, 129, 0.5)',
                    wickDownColor: 'rgba(239, 68, 68, 0.5)',
                });
                futureSeries.setData(futurePath);
            }
            // Fallback to single predicted candle if no path
            else if (predictedCandle) {
                const lastTime = data[data.length - 1].time;
                const predictedTime = new Date(new Date(lastTime).getTime() + 86400000).toISOString().split('T')[0];

                const predictionData = [{
                    time: predictedTime,
                    open: predictedCandle.open,
                    high: predictedCandle.high,
                    low: predictedCandle.low,
                    close: predictedCandle.close,
                }];

                const predictionSeries = chart.addSeries(CandlestickSeries, {
                    upColor: 'rgba(16, 185, 129, 0.3)',
                    downColor: 'rgba(239, 68, 68, 0.3)',
                    borderVisible: true,
                    borderUpColor: '#10B981',
                    borderDownColor: '#EF4444',
                    wickUpColor: 'rgba(16, 185, 129, 0.5)',
                    wickDownColor: 'rgba(239, 68, 68, 0.5)',
                });
                predictionSeries.setData(predictionData);
            }

            // Add stop loss and target price lines
            if (tradeLevels) {
                // Stop Loss Line (Red)
                const stopLossSeries = chart.addSeries(LineSeries, {
                    color: '#EF4444',
                    lineWidth: 2,
                    lineStyle: 2, // Dashed
                    title: `Stop Loss: ${tradeLevels.stop_loss}`,
                    priceLineVisible: false,
                    lastValueVisible: true,
                });

                const stopLossData = data.map(d => ({
                    time: d.time,
                    value: tradeLevels.stop_loss
                }));
                stopLossSeries.setData(stopLossData);

                // Target Price Line (Green)
                const targetSeries = chart.addSeries(LineSeries, {
                    color: '#10B981',
                    lineWidth: 2,
                    lineStyle: 2, // Dashed
                    title: `Target: ${tradeLevels.target_price}`,
                    priceLineVisible: false,
                    lastValueVisible: true,
                });

                const targetData = data.map(d => ({
                    time: d.time,
                    value: tradeLevels.target_price
                }));
                targetSeries.setData(targetData);

                // Entry Price Line (Yellow)
                const entrySeries = chart.addSeries(LineSeries, {
                    color: '#FBBF24',
                    lineWidth: 1,
                    lineStyle: 0, // Solid
                    title: `Entry: ${tradeLevels.entry_price}`,
                    priceLineVisible: false,
                    lastValueVisible: true,
                });

                const entryData = data.map(d => ({
                    time: d.time,
                    value: tradeLevels.entry_price
                }));
                entrySeries.setData(entryData);
            }
        }

        chartRef.current = chart;

        const handleResize = () => {
            chart.applyOptions({ width: chartContainerRef.current.clientWidth });
        };

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, [data, tradeLevels, predictedCandle, futurePath]);

    return (
        <div className="relative w-full h-full">
            <div ref={chartContainerRef} className="w-full h-full" />

            {/* Council Overlay */}
            {council && (
                <div className="absolute top-4 left-4 bg-gray-900/90 p-4 rounded-xl border border-gray-700 backdrop-blur-sm max-w-xs z-10">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="font-bold text-white flex items-center gap-2">
                            🤖 Council of Agents
                        </h3>
                        <span className={`px-2 py-0.5 rounded text-xs font-bold ${council.consensus === 'BUY' ? 'bg-green-500/20 text-green-400' :
                            council.consensus === 'SELL' ? 'bg-red-500/20 text-red-400' :
                                'bg-gray-500/20 text-gray-400'
                            }`}>
                            {council.consensus}
                        </span>
                    </div>

                    <div className="space-y-2">
                        {Object.entries(council.votes).map(([agent, data]) => (
                            <div key={agent} className="flex items-center justify-between text-xs">
                                <span className="text-gray-400">{agent}</span>
                                <div className="flex items-center gap-2">
                                    <span className={`font-medium ${data.vote === 'BUY' ? 'text-green-400' :
                                        data.vote === 'SELL' ? 'text-red-400' :
                                            'text-gray-500'
                                        }`}>
                                        {data.vote}
                                    </span>
                                    <div className="w-12 h-1 bg-gray-700 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-blue-500"
                                            style={{ width: `${data.confidence * 100}%` }}
                                        />
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Chart;
