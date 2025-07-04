// Performance hook for managing animations and reduced motion
import { useState, useEffect, useMemo } from 'react';

export const usePerformanceSettings = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const [isHighPerformance, setIsHighPerformance] = useState(true);

  useEffect(() => {
    // Check for reduced motion preference
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (e) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handleChange);

    // Check device performance indicators
    const checkPerformance = () => {
      const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
      const isSlowConnection = connection && (
        connection.effectiveType === 'slow-2g' || 
        connection.effectiveType === '2g' ||
        connection.saveData
      );

      const isLowEndDevice = navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 2;
      const hasLimitedMemory = navigator.deviceMemory && navigator.deviceMemory <= 2;

      setIsHighPerformance(!isSlowConnection && !isLowEndDevice && !hasLimitedMemory);
    };

    checkPerformance();

    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Animation configurations based on performance
  const animationConfig = useMemo(() => {
    if (prefersReducedMotion) {
      return {
        duration: 0,
        enabled: false,
        reduceComplexity: true
      };
    }

    if (!isHighPerformance) {
      return {
        duration: 150,
        enabled: true,
        reduceComplexity: true
      };
    }

    return {
      duration: 300,
      enabled: true,
      reduceComplexity: false
    };
  }, [prefersReducedMotion, isHighPerformance]);

  return {
    prefersReducedMotion,
    isHighPerformance,
    animationConfig,
    shouldAnimate: animationConfig.enabled && !prefersReducedMotion
  };
};
